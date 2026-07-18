from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from modules.load_vectorstore import load_vectorstore
from fastapi.responses import JSONResponse
from logger import logger
from pinecone import Pinecone
import os


router = APIRouter()

@router.post("/upload_pdfs/")
async def upload_pdfs(files : List[UploadFile] = File(...)):
    try:
        logger.info("Received uploaded files")
        # Before loading, ensure any existing vectors for these files are removed
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        for f in files:
            src = f"uploaded_docs/{f.filename}"
            try:
                logger.info(f"Deleting existing vectors for {src}")
                index.delete(filter={"source": src})
            except Exception:
                logger.exception(f"Failed to delete existing vectors for {src}")
        # now proceed to load and upsert
        load_vectorstore(files)
        logger.info("Document added to vectorstore")
        return {"message" : "Files processes and vectorstore updated"}
    except Exception as e:
        logger.exception("Error during PDF upload")
        return JSONResponse(status_code=500, content = {"error" : str(e)})


@router.post("/delete_pdf/")
async def delete_pdf(filename: str = Form(...)):
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        src = f"uploaded_docs/{filename}"
        logger.info(f"Deleting vectors for {src}")
        index.delete(filter={"source": src})
        # remove the file if present
        file_path = os.path.join(os.getcwd(), "uploaded_docs", filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed file {file_path}")
        return {"message": f"Deleted vectors and file for {filename}"}
    except Exception as e:
        logger.exception("Error deleting PDF vectors")
        return JSONResponse(status_code=500, content={"error": str(e)})