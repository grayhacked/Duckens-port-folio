"""Limiteur de débit partagé (slowapi) : identifie chaque client par son adresse IP."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
