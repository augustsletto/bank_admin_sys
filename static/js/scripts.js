document.addEventListener("DOMContentLoaded", function () {
    const darkModeOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#ffffff",
                    font: { size: 14 }
                }
            }
        },
        scales: {
            x: {
                ticks: { color: "#bbbbbb" },
                grid: { color: "rgba(255, 255, 255, 0.1)" }
            },
            y: {
                ticks: { color: "#bbbbbb" },
                grid: { color: "rgba(255, 255, 255, 0.1)" }
            }
        }
    };

    // Ensure elements exist before initializing charts
    if (document.getElementById("lineChart")) {
        new Chart(document.getElementById("lineChart"), {
            type: "line",
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                datasets: [
                    {
                        data: [10, 25, 15, 40, 30, 50],
                        borderColor: "#00c3ff",
                        backgroundColor: "rgba(0, 195, 255, 0.2)",
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 4
                    },
                    {
                        data: [20, 15, 35, 25, 45, 55],
                        borderColor: "#ff5733",
                        backgroundColor: "rgba(255, 87, 51, 0.2)",
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 4
                    }
                ]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { display: true } }
                }
            }
        });
    }

    if (document.getElementById("barChart")) {
        new Chart(document.getElementById("barChart"), {
            type: "bar",
            data: {
                labels: ["Red", "Blue", "Yellow", "Green", "Purple"],
                datasets: [
                    {
                        data: [12, 15, 3, 5, 2],
                        backgroundColor: ["#ff6b6b", "#4d96ff", "#ffd93d", "#4caf50", "#9c27b0"],
                        borderRadius: 6
                    },
                    {
                        data: [9, 14, 5, 7, 13],
                        backgroundColor: ["#ff6b6b", "#4d96ff", "#ffd93d", "#4caf50", "#9c27b0"],
                        borderRadius: 6
                    }
                ]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { display: false } },
                    y: { grid: { display: false }, ticks: { display: false } }
                }
            }
        });
    }

    // Currency Converter Functions
    function convertCurrency() {
        let amount = parseFloat(document.getElementById("amount").value);
        let fromCurrency = document.getElementById("fromCurrency").value;
        let toCurrency = document.getElementById("toCurrency").value;

        fetch(`/convert?amount=${amount}&from=${fromCurrency}&to=${toCurrency}`)
            .then(response => response.json())
            .then(data => {
                if (data.converted_amount !== undefined) {
                    document.getElementById("convertedAmount").value = data.converted_amount;
                } else {
                    alert("Error: " + JSON.stringify(data));
                }
            })
            .catch(error => console.error("Error:", error));
    }
    

    function addNumber(num) {
        document.getElementById("amount").value += num;
    }

    function clearAmount() {
        document.getElementById("amount").value = "";
    }

    // Expose functions to global scope if needed
    window.convertCurrency = convertCurrency;
    window.addNumber = addNumber;
    window.clearAmount = clearAmount;
});
