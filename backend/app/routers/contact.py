"""POST /contact : reçoit un message du formulaire, l'enregistre et me l'envoie par email."""
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, EmailStr, Field

from ..config import settings
from ..limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["contact"])

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


class ContactIn(BaseModel):
    """Corps de la requête, validé automatiquement par Pydantic (sinon réponse 422)."""

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=3000)
    website: str = ""  # pot de miel : champ caché que seuls les robots remplissent


def save_message(msg: ContactIn) -> None:
    """Copie de secours en SQLite (bloquant : appelé hors de la boucle async)."""
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.db_path) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS messages "
            "(created_at TEXT, name TEXT, email TEXT, message TEXT)"
        )
        db.execute(
            "INSERT INTO messages VALUES (?, ?, ?, ?)",  # requête paramétrée : pas d'injection SQL
            (datetime.now(timezone.utc).isoformat(), msg.name, msg.email, msg.message),
        )


async def send_email(msg: ContactIn) -> None:
    """Envoie le message via l'API Brevo. Sans clé configurée, ne fait rien."""
    if not settings.brevo_api_key:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            BREVO_URL,
            headers={"api-key": settings.brevo_api_key},
            json={
                "sender": {"name": "Portfolio", "email": settings.contact_from},
                "to": [{"email": settings.contact_to}],
                "replyTo": {"email": msg.email, "name": msg.name},
                "subject": f"[Portfolio] Message de {msg.name}",
                "textContent": f"{msg.message}\n\n— {msg.name} <{msg.email}>",
            },
        )
        response.raise_for_status()


@router.post("/contact", status_code=202)
@limiter.limit(lambda: settings.contact_rate_limit)
async def contact(request: Request, payload: ContactIn) -> dict:
    # `request` est obligatoire : slowapi en a besoin pour lire l'IP du client.
    if payload.website:
        # Robot détecté : on répond "ok" pour ne pas lui apprendre qu'il a été filtré.
        return {"ok": True}

    await run_in_threadpool(save_message, payload)
    try:
        await send_email(payload)
    except httpx.HTTPError:
        logger.exception("Échec de l'envoi de l'email via Brevo")
        raise HTTPException(
            status_code=502,
            detail="Envoi impossible pour le moment. Écrivez-moi directement par email.",
        )
    return {"ok": True}
