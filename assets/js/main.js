// Bouton de thème clair / sombre, ajouté à la navigation de chaque page.
// Le choix est mémorisé dans localStorage ; sinon le thème du système s'applique.
(function () {
    var root = document.documentElement;
    var nav = document.querySelector('header nav');
    if (!nav) return;

    var media = window.matchMedia('(prefers-color-scheme: dark)');

    function currentTheme() {
        return root.getAttribute('data-theme') || (media.matches ? 'dark' : 'light');
    }

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'theme-toggle';

    function render() {
        var dark = currentTheme() === 'dark';
        button.textContent = dark ? '☀' : '☾';
        button.setAttribute('aria-label', dark ? 'Passer au thème clair' : 'Passer au thème sombre');
        button.title = button.getAttribute('aria-label');
    }

    button.addEventListener('click', function () {
        var next = currentTheme() === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        try { localStorage.setItem('theme', next); } catch (e) { /* stockage indisponible */ }
        render();
    });

    if (media.addEventListener) media.addEventListener('change', render);

    render();
    nav.appendChild(button);
})();
