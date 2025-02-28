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


        if (document.getElementById("doughnutChart")) {
            let ctx = document.getElementById("doughnutChart").getContext("2d");
        
            let doughnutChartData = JSON.parse(document.getElementById("doughnutChartData").textContent);
        
            new Chart(ctx, {
                type: "doughnut",
                data: doughnutChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: "#ffffff", 
                                font: { size: 14 }
                            }
                        }
                    }
                }
            });
        }
        


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




function changeCardColor(primary, secondary) {
    document.getElementById('creditCard').style.background = `linear-gradient(135deg, ${primary}, ${secondary})`;
}




// Customer.html scripts

let currentPage = 2;
let customerId = "{{ customer.id }}"
let selectedAccountId = "{{ selected_account_id }}"

    

function loadMoreTransactions() {
    fetch(`/customer/${customerId}/transactions?account_id=${selectedAccountId}&page=${currentPage}`)
    .then(response => response.json())
    .then(data => {
        if (data.transactions.length > 0) {
            let table = document.getElementById("transaction-table");

            data.transactions.forEach(t => {
                
                let row = table.insertRow();
                row.innerHTML = `
                <td>${t.id}</td>
                <td>${t.date}</td>
                <td>${t.operation}</td>
                <td class="text-end ${t.type === 'Debit' ? 'text-success' : 'text-danger'}">
                    ${t.type === 'Debit' ? '' : '-'} $${t.amount}
                </td>
                `;
            });
            if (!data.has_more) {
                document.getElementById("load-more-btn").style.display = "none"
            }
        }
        currentPage++;
    })
    .catch(error => console.error("Error loading more transactions:", error));
}





// Add Customer color toggle
function changeCardColor(primary, secondary) {
    document.getElementById('creditCard').style.background = `linear-gradient(135deg, ${primary}, ${secondary})`;
}



