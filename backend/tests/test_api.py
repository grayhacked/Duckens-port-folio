import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.limiter import limiter
from app.main import app
from app.routers import contact as contact_module
from app.routers import forecast as forecast_module

client = TestClient(app)

VALID_MESSAGE = {"name": "Recruteur", "email": "rh@exemple.fr", "message": "Bonjour, votre profil nous intéresse."}


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Chaque test : base SQLite temporaire, aucun email réel, compteurs anti-spam remis à zéro."""
    monkeypatch.setattr(settings, "db_path", str(tmp_path / "test.db"))
    monkeypatch.setattr(settings, "brevo_api_key", "")
    limiter.reset()
    forecast_module.load_demo.cache_clear()
    yield
    forecast_module.load_demo.cache_clear()


# ---------- /health ----------
def test_health():
    assert client.get("/health").json() == {"status": "ok"}


# ---------- /contact ----------
def test_contact_ok_enregistre_le_message():
    r = client.post("/contact", json=VALID_MESSAGE)
    assert r.status_code == 202
    import sqlite3
    with sqlite3.connect(settings.db_path) as db:
        assert db.execute("SELECT name, email FROM messages").fetchall() == [("Recruteur", "rh@exemple.fr")]


@pytest.mark.parametrize("champ, valeur", [("email", "pas-un-email"), ("message", "court"), ("name", "")])
def test_contact_refuse_les_donnees_invalides(champ, valeur):
    r = client.post("/contact", json={**VALID_MESSAGE, champ: valeur})
    assert r.status_code == 422


def test_contact_pot_de_miel_ignore_les_robots():
    r = client.post("/contact", json={**VALID_MESSAGE, "website": "http://spam.example"})
    assert r.status_code == 202
    import os
    assert not os.path.exists(settings.db_path)  # rien n'a été enregistré


def test_contact_limite_de_debit(monkeypatch):
    monkeypatch.setattr(settings, "contact_rate_limit", "2/minute")
    assert client.post("/contact", json=VALID_MESSAGE).status_code == 202
    assert client.post("/contact", json=VALID_MESSAGE).status_code == 202
    assert client.post("/contact", json=VALID_MESSAGE).status_code == 429


def test_contact_erreur_brevo_renvoie_502(monkeypatch):
    async def echec(_msg):
        raise httpx.ConnectError("Brevo injoignable")

    monkeypatch.setattr(contact_module, "send_email", echec)
    assert client.post("/contact", json=VALID_MESSAGE).status_code == 502


# ---------- /forecast/demo ----------
# Données factices propres aux tests (jamais affichées sur le site).
SAMPLE = {"title": "Test", "unit": "°C", "model": "XGBRegressor", "mae": 1.2,
          "dates": ["2025-01-01", "2025-01-02"], "actual": [10.0, 11.0], "forecast": [10.5, 10.8]}


def use_demo_file(monkeypatch, tmp_path, content: str):
    """Fait pointer l'endpoint vers un fichier temporaire au lieu du vrai forecast_demo.json."""
    path = tmp_path / "demo.json"
    path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(forecast_module, "DATA_PATH", path)


def test_forecast_demo_ok(monkeypatch, tmp_path):
    use_demo_file(monkeypatch, tmp_path, json.dumps(SAMPLE))
    r = client.get("/forecast/demo")
    assert r.status_code == 200
    assert r.json()["forecast"] == [10.5, 10.8]


@pytest.mark.parametrize("contenu", ["", "{pas du json", json.dumps({**SAMPLE, "actual": [1.0]})])
def test_forecast_demo_fichier_absent_ou_invalide_renvoie_503(monkeypatch, tmp_path, contenu):
    use_demo_file(monkeypatch, tmp_path, contenu)
    assert client.get("/forecast/demo").status_code == 503
