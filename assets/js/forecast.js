// Démo de prévision : récupère GET /forecast/demo et trace prévu vs observé avec Chart.js.
// La section n'apparaît que si l'API répond avec de vraies données.
(function () {
    var section = document.getElementById('forecast-demo');
    var canvas = document.getElementById('forecast-chart');
    if (!section || !canvas || !window.API_BASE || !window.Chart) return;

    var caption = document.getElementById('demo-caption');
    var css = getComputedStyle(document.documentElement);
    var color = function (name) { return css.getPropertyValue(name).trim(); };

    fetch(window.API_BASE + '/forecast/demo')
        .then(function (response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
        })
        .then(function (demo) {
            caption.textContent = demo.title + ' · modèle ' + demo.model + ' · MAE ' + demo.mae + ' ' + demo.unit;
            section.hidden = false;
            new Chart(canvas, {
                type: 'line',
                data: {
                    labels: demo.dates,
                    datasets: [
                        { label: 'Observé', data: demo.actual, borderColor: color('--muted'), backgroundColor: color('--muted'), borderWidth: 2, pointRadius: 0 },
                        { label: 'Prévu', data: demo.forecast, borderColor: color('--accent'), backgroundColor: color('--accent'), borderWidth: 2, pointRadius: 0, borderDash: [6, 4] }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: { mode: 'index', intersect: false },
                    plugins: { legend: { labels: { color: color('--text') } } },
                    scales: {
                        x: { ticks: { color: color('--muted'), maxTicksLimit: 8 }, grid: { color: color('--border') } },
                        y: { ticks: { color: color('--muted') }, grid: { color: color('--border') },
                             title: { display: true, text: demo.unit, color: color('--muted') } }
                    }
                }
            });
        })
        .catch(function () { /* démo indisponible : la section reste masquée */ });
})();
