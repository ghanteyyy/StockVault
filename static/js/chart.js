let chartInstance = null;


function renderLineChart(id, title, labels, data, border_color="rgba(30,144,255,1)", bg_color="rgba(30,144,255,0.4)") {
    console.log(id, title, labels, data)

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
                borderColor: border_color,
                backgroundColor: bg_color,
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
                        label: (ctx) => `${ctx.parsed.y}`
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

window.renderLineChart = renderLineChart;

