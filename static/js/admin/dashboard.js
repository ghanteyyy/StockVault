window.Chart || document.write('<script src="/path/to/local/chart.min.js"><\/script>');

document.addEventListener('DOMContentLoaded', function() {
    function triggerFileInput() {
        const fileInput = document.getElementById('profileImage');
        if (fileInput) {
            fileInput.click();
        }
    }

    window.triggerFileInput = triggerFileInput;

    const profileImageInput = document.getElementById('profileImage');
    if (profileImageInput) {
        profileImageInput.addEventListener('change', function(e) {
            try {
                if (e.target.files.length > 0) {
                    const file = e.target.files[0];
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const profileImg = document.querySelector('.user-profile img');
                        if (profileImg) {
                            profileImg.src = e.target.result;
                        }
                    };
                    reader.onerror = function() {
                        console.error('Error reading file');
                    };
                    reader.readAsDataURL(file);
                }
            } catch (err) {
                console.error('Error handling file input:', err);
            }
        });
    }

    try {
        const transactionCanvas = document.getElementById('transactionChart');
        if (!transactionCanvas) {
            console.error('Transaction chart canvas not found');
            return;
        }

        new Chart(transactionCanvas, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Transaction Volume ($)',
                    data: [500000, 600000, 550000, 700000, 650000, 800000],
                    backgroundColor: '#1a3c34'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                },
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    } catch (err) {
        console.error('Error initializing transaction chart:', err);
    }
});
