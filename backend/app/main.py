"""Point d'entrée de l'API du portfolio."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .limiter import limiter
from .routers import contact, forecast

app = FastAPI(
    title="API Portfolio – Jean Duckens Sannon",
    description="Formulaire de contact et démo de prévision du portfolio.",
    version="1.0.0",
)

# Limitation de débit : slowapi lit le limiteur dans app.state
# et transforme un dépassement en réponse HTTP 429.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS : seul le site du portfolio (et Live Server en local) peut appeler l'API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(contact.router)
app.include_router(forecast.router)


@app.get("/health", tags=["monitoring"])
def health() -> dict:
    """Utilisé par Render pour vérifier que le service répond."""
    return {"status": "ok"}
