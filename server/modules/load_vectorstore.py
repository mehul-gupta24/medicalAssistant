import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medical-index"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# initialize pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region = PINECONE_ENV)
existing_index = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_index:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=3072,
        metric="dotproduct",
        spec=spec
    )
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1) #1 second

index=pc.Index(PINECONE_INDEX_NAME)

# load, split, embed and upsert pdf docs content

def load_vectorstore(uploaded_files):
    index.delete(delete_all=True)
    print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
    embed_models = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-001")
    file_paths = []

    # 1 upload
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR)/file.filename
        with open(save_path,"wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    # 2 split
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        # metadata = [chunk.metadata for chunk in chunks]
        metadata = [
                    {
                        **chunk.metadata,
                        "text": chunk.page_content
                    }
                    for chunk in chunks
                ]
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        
        # Embedding
        print(f"Embedding chunks")
        embedding = embed_models.embed_documents(texts)

        # Upsert
        print(f"Upserting Embeddings")
        
        print(metadata[0])

        with tqdm(total = len(embedding), desc = "Upserting to Pinacone") as progress:
            # Convert zip to list to ensure the Pinecone client receives a concrete list
            to_upsert = list(zip(ids, embedding, metadata))
            index.upsert(vectors=to_upsert)
            progress.update(len(embedding))

        print(f"Upload complete for {file_path}")
