from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as ask_router

app = FastAPI(title = "Medical Assistant API", description = "API for AI medical assistant chatbot")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)


# middleware exception handlers
app.middleware("http")(catch_exception_middleware)

# routers
# - upload pdf doc
app.include_router(upload_router)
# - asking queries
app.include_router(ask_router)