// Formulaire de contact : envoie le message à POST /contact de l'API.
(function () {
    var section = document.getElementById('contact-form-section');
    var form = document.getElementById('contact-form');
    if (!section || !form || !window.API_BASE) return; // API non configurée : section laissée masquée

    section.hidden = false;
    var status = document.getElementById('form-status');
    var button = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        if (!form.reportValidity()) return; // validation native du navigateur

        button.disabled = true;
        status.textContent = 'Envoi en cours… (le premier envoi peut prendre jusqu’à une minute)';

        try {
            var response = await fetch(window.API_BASE + '/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(Object.fromEntries(new FormData(form)))
            });
            if (response.status === 429) throw new Error('Trop de messages envoyés. Réessayez dans une heure.');
            if (response.status === 422) throw new Error('Vérifiez les champs : email valide et message d’au moins 10 caractères.');
            if (!response.ok) throw new Error('Envoi impossible. Écrivez-moi à sannonjeanduckens@gmail.com.');

            form.reset();
            status.textContent = 'Merci ! Votre message a bien été envoyé.';
        } catch (error) {
            // fetch lève une TypeError si l'API est injoignable (réseau, CORS)
            status.textContent = error instanceof TypeError
                ? 'Service momentanément injoignable. Écrivez-moi à sannonjeanduckens@gmail.com.'
                : error.message;
        } finally {
            button.disabled = false;
        }
    });
})();
