"""Configuration de l'API, lue depuis les variables d'environnement (ou le fichier .env en local)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Origines autorisées à appeler l'API depuis un navigateur (CORS).
    # Dans .env ou sur Render, au format JSON : ["https://grayhacked.github.io"]
    allowed_origins: list[str] = ["http://127.0.0.1:5500", "http://localhost:5500"]

    # Envoi d'email via l'API Brevo. Clé vide = pas d'envoi (local, tests).
    brevo_api_key: str = ""
    contact_to: str = "sannonjeanduckens@gmail.com"
    contact_from: str = ""  # adresse expéditrice validée dans Brevo

    # Base SQLite de secours pour les messages reçus.
    db_path: str = "data/messages.db"

    # Limite anti-spam du formulaire de contact, par adresse IP.
    contact_rate_limit: str = "5/hour"


settings = Settings()
