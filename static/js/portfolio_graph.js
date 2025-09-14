let chartInstance = null;


function renderLineChart(id, title, labels, data) {
    const ctx = document.getElementById(id);

    if(chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'LTP',
                data: data,
                fill: true,
                borderColor: "rgba(30,144,255,1)",
                backgroundColor: "rgba(30,144,255,0.4)",
                tension: 0.3,
                pointRadius: 0,
                pointHoverRadius: 4,
                pointHitRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: title.toUpperCase(),
                    color: '#333',
                    font: { size: 18, weight: 'bold' },
                    padding: { top: 10, bottom: 20 }
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: (ctx) => `Date: ${ctx.label} | ${column_type}: ${ctx.parsed.y}`
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                intersect: false
            },
            scales: {
                x: {
                    grid: { display: false, drawBorder: false, drawTicks: false },
                    ticks: { display: false }
                },
                y: { beginAtZero: false }
            }
        }
    });
}


params = new URLSearchParams(window.location.search);
column_type = params.get("column_type") || "LTP";


renderLineChart('graph1', column_type, labels, data);


document.getElementById('graph_options').addEventListener('change', function() {
    const params = new URLSearchParams(window.location.search);
    params.set('column_type', this.value);

    const url = window.location.origin + window.location.pathname + '?' + params.toString();
    window.location.href = url;
});

