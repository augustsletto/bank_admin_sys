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

    
    if (document.getElementById("lineChart")) {
        let ctx = document.getElementById("lineChart").getContext("2d");

        let chartData = JSON.parse(document.getElementById("chartData").textContent);

        

        new Chart(ctx, {
            type: "line",
            data: chartData,
            options: {
                plugins: { legend: {
                     display: true },
                     labels: {
                    color: "#ffffff",
                    font: { size: 14 }
                }
                    },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { display: true } }
                }
            }
        })};


    if (document.getElementById("barChart")) {
        let bctx = document.getElementById("barChart").getContext("2d");
        
        let barChartData = JSON.parse(document.getElementById("barChartData").textContent)
        new Chart(bctx, {
            type: "bar",
            data: barChartData,
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { display: true } },
                    y: { grid: { display: false }, ticks: { display: false } }
                }
            }
        })};
    
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

    
    window.convertCurrency = convertCurrency;
    window.addNumber = addNumber;
    window.clearAmount = clearAmount;
});
