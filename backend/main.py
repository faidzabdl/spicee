from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="SPICEE API",
    description="Backend API untuk aplikasi UMKM rempah dan produk khas Indonesia",
    version="1.0.0",
)

# CORS — allow frontend React/Flutter
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
origins = [o.strip() for o in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "SPICEE API"}


# Import routers (akan ditambahkan per sub-task)
from routers import transaksi, hpp, chat  # noqa: E402

app.include_router(transaksi.router)
app.include_router(hpp.router)
app.include_router(chat.router)
