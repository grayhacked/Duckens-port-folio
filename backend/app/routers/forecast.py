"""GET /forecast/demo : prévisions pré-calculées du projet météo, affichées en graphique sur le site."""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError, model_validator

router = APIRouter(tags=["forecast"])

DATA_PATH = Path(__file__).resolve().parent.parent / "models" / "forecast_demo.json"


class ForecastDemo(BaseModel):
    """Format attendu du fichier exporté depuis le projet météo."""

    title: str
    unit: str
    model: str
    mae: float
    dates: list[str]
    actual: list[float]
    forecast: list[float]

    @model_validator(mode="after")
    def same_length(self) -> "ForecastDemo":
        if not (len(self.dates) == len(self.actual) == len(self.forecast)):
            raise ValueError("dates, actual et forecast doivent avoir la même longueur")
        return self


@lru_cache
def load_demo() -> ForecastDemo:
    """Lu et validé une seule fois, puis gardé en mémoire (lru_cache).
    En cas d'erreur rien n'est mis en cache : le prochain appel réessaie."""
    return ForecastDemo.model_validate(json.loads(DATA_PATH.read_text(encoding="utf-8")))


@router.get("/forecast/demo", response_model=ForecastDemo)
def forecast_demo() -> ForecastDemo:
    try:
        return load_demo()
    except (FileNotFoundError, json.JSONDecodeError, ValidationError):
        # Fichier absent, vide ou mal formé : la démo n'est pas encore prête.
        raise HTTPException(status_code=503, detail="Démo de prévision pas encore disponible.")
