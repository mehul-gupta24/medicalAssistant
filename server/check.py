from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

embed = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

vec = embed.embed_query("hello")
print(len(vec))