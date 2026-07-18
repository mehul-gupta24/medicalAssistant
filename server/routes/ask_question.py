from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from modules.llm import get_llm_chain
from modules.query_handlers import query_chain

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
import os
from langchain_community.document_loaders import PyPDFLoader

router = APIRouter()

@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        logger.info(f"User query : {question}")

        # If no local PDFs have been uploaded, return a friendly prompt
        upload_dir = os.path.join(os.getcwd(), "uploaded_docs")
        if not os.path.exists(upload_dir) or len(os.listdir(upload_dir)) == 0:
            return JSONResponse(status_code=200, content={
                "response": "Hi! 👋 I'm your Medical Assistant. Please upload a medical PDF first so I can answer questions based on your documents.",
                "sources": []
            })

        # embed model + pinecone setup
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        # stats = index.describe_index_stats()
        embed_model = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-001")
        embedded_query = embed_model.embed_query(question)
        res = index.query(vector = embedded_query, top_k=3, include_metadata=True)
        print(res)

        docs = []
        for match in res.get("matches", []):
            meta = match.get("metadata", {}) or {}
            text = meta.get("text", "")
            # fallback: try to load text from local source file if available
            if not text and meta.get("source"):
                try:
                    src_path = meta.get("source")
                    # If stored path is relative to server root, make sure to use correct path
                    if not os.path.isabs(src_path):
                        src_path = os.path.join(os.getcwd(), src_path)
                    loader = PyPDFLoader(src_path)
                    pages = loader.load()
                    # join all pages as fallback context
                    text = "\n".join([p.page_content for p in pages])
                    logger.debug(f"Loaded fallback text from {src_path}")
                except Exception:
                    logger.exception(f"Failed to load fallback text from source: {meta.get('source')}")

            docs.append(Document(page_content=text, metadata=meta))
        print("DOCS:", docs)
        for d in docs:
            print("PAGE:", d.page_content)

        print("Matches:", len(res.matches))
        print(res.matches)
        # If no documents were returned from the vectorstore, provide a clearer debug response
        if not docs:
            logger.info("No documents matched the query")
            # return JSONResponse(status_code=200, content={
            #     "response": "No documents matched the query. Make sure PDFs were uploaded and indexed.",
            #     "debug": res
            # })
            return {
            "response": "Hi! 👋 I'm your Medical Assistant. Please upload a medical PDF first so I can answer questions based on your documents."}

        class SimpleRetrieval(BaseRetriever):
            tags: Optional[List[str]] = Field(default_factory=list)
            metadata: Optional[dict] = Field(default_factory=dict)
            def __init__(self, documents : List[Document]):
                super().__init__()
                self._docs = documents
            def get_relevant_documents(self, query: str) -> List[Document]:
                return self._docs
        
        retriever = SimpleRetrieval(docs)
        chain = get_llm_chain(retriever)
        result = query_chain(chain, question)
        logger.info("Query is successful")
        return result

    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(status_code=500, content={"error":str(e)})