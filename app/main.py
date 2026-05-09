from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import hotel, chat
from app.database import init_db

app = FastAPI(title="Hotel AI Receptionist")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    try:
        init_db()
    except Exception as e:
        print(f"[WARNING] DB not available: {e}")

app.include_router(hotel.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Hotel AI Receptionist is running"}
