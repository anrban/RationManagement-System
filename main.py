import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import auth, beneficiaries, distributions, analytics, admin  # noqa: E402

app = FastAPI(
    title="Digital Ration Management System",
    description="Government-grade welfare tracking system to eliminate leakages and duplication",
    version="1.0.0",
)

# ─── CORS ────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(beneficiaries.router, prefix="/beneficiaries", tags=["Beneficiaries"])
app.include_router(distributions.router, prefix="/distributions", tags=["Distributions"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


# ─── Health Check ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Digital Ration Management System"}
