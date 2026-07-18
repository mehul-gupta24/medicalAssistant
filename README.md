# Medical AI Assistant (RAG Pipeline)

This project implements a modular, Retrieval-Augmented Generation (RAG) system designed to act as a medical document assistant. It allows users to upload PDF medical files, process them, and ask precise, context-aware questions based on the content.

## Technical Architecture
*   **Frontend:** Streamlit (deployed on Streamlit Cloud)
*   **Backend:** FastAPI (deployed on Render)
*   **LLM:** Groq Llama 3 (70B parameters)
*   **Vector Database:** Pinecone (Serverless)
*   **Embedding Model:** Google Generative AI Embeddings (`models/embedding-001`)
*   **Orchestration:** LangChain

## Core Features
*   **Dynamic Document Processing:** Handles PDF uploads, performs text chunking (using `RecursiveCharacterTextSplitter`), and generates vector embeddings.
*   **Efficient Retrieval:** Uses Pinecone as a cloud-based vector store for fast, scalable information retrieval.
*   **Interactive Chat:** A custom-built Streamlit interface that maintains conversation history and allows for chat history exports.
*   **Robust Backend:** FastAPI-based server providing dedicated API endpoints for file uploads and querying.
*   **Observability:** Integrated logging module for monitoring and debugging processes in real-time.

## Prerequisites
*   Python (Project managed via `uv`)
*   API Keys:
    *   [Google Gemini API Key](https://aistudio.google.com/)
    *   [Pinecone API Key](https://www.pinecone.io/)
    *   [Groq API Key](https://console.groq.com/)

## Project Structure
```text
├── server/
│   ├── main.py          # FastAPI entry point
│   ├── logger.py        # Logging configuration
│   ├── modules/         # Business logic (LLM chains, vector stores)
│   └── routes/          # API endpoints (Upload, Query)
├── client/
│   ├── app.py           # Streamlit UI
│   ├── components/      # UI widgets (Chat, Uploader, Downloads)
│   ├── utils/           # API request handlers
│   └── config.py        # Configuration settings
└── .env                 # Environment variables (Do not commit)