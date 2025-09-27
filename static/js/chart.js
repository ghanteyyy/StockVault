window.charts = window.charts || {};


function renderLineChart(id, title, labels, data) {
    const canvas = document.getElementById(id);
    if (!canvas) return;

    const existing = Chart.getChart(id);
    if (existing){
        existing.destroy();
    }

    const ctx = canvas.getContext("2d");

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'LTP',
                data: data.map(v => +String(v).replace(/,/g, '')),
                fill: true,
                tension: 0.3,
                pointRadius: 0,
                pointHitRadius: 8,
                pointHoverRadius: 4,
                borderColor: "rgba(30,144,255,1)",
                backgroundColor: "rgba(30,144,255,0.4)",
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: String(title).toUpperCase(),
                    color: '#333',
                    font: { size: 18, weight: 'bold' },
                    padding: { top: 10, bottom: 20 }
                },
                tooltip: {
                    enabled: true,
                    callbacks: { label: (ctx) => `${ctx.parsed.y}` }
                }
            },
            interaction: { mode: 'nearest', intersect: false },
            scales: {
                x: { grid: { display: false, drawBorder: false, drawTicks: false }, ticks: { display: false } },
                y: { beginAtZero: false }
            }
        }
    });

    window.charts[id] = chart;

    return chart;
}


function updateLineChartById(id, title, labels, data, { animate = false } = {}) {
    const chart = Chart.getChart(id) || (window.charts && window.charts[id]);
    if (!chart) {
        renderLineChart(id, title, labels, data);
        return;
    }

    try { chart.stop(); } catch { }

    chart.data.labels.splice(0, chart.data.labels.length, ...labels);

    const ds = chart.data.datasets[0] || chart.data.datasets[chart.data.datasets.length - 1];
    const numeric = data.map(v => +String(v).replace(/,/g, ''));
    ds.data.splice(0, ds.data.length, ...numeric);

    if (chart.options?.plugins?.title) {
        chart.options.plugins.title.text = String(title).toUpperCase();
    }

    chart.update(animate ? undefined : 'none');
}



window.renderLineChart = renderLineChart;
window.updateLineChartById = updateLineChartById;
