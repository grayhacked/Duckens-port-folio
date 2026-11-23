// Adresse de l'API backend (FastAPI).
// En local (Live Server) : l'API lancée avec `uvicorn app.main:app --reload`.
// En ligne : remplacez la chaîne vide par l'URL Render, ex. 'https://portfolio-api-xxxx.onrender.com'.
// Tant qu'elle est vide, le formulaire et la démo restent masqués sur le site.
(function () {
    var PRODUCTION_API = '';
    var local = location.hostname === '127.0.0.1' || location.hostname === 'localhost';
    window.API_BASE = local ? 'http://127.0.0.1:8000' : PRODUCTION_API;
})();
