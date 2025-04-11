document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("strategy-form");
    const strategyTypeRadios = document.getElementsByName("product_type");
   
    const tickerSelect = document.getElementById("ticker");
    const tickerPriceInput = document.getElementById("ticker-price");
    const resultPrice = document.getElementById("price");
    const spinner = document.getElementById("loading-spinner");

    // Fonction pour récupérer le prix du ticker
    function fetchTickerPrice() {
        fetch(`/get_ticker_price?ticker=${tickerSelect.value}`)
            .then(response => response.json())
            .then(data => tickerPriceInput.value = data.ticker_price)
            .catch(err => console.error("Erreur récupération ticker:", err));
    }

    // Fonction pour rendre le graphique du payoff
    function renderPayoffChart(payoffData) {
        const ctx = document.getElementById('payoffChart').getContext('2d');
    
        // Si un graphique existe déjà, on le détruit pour en recréer un propre
        if (window.payoffChartInstance) {
            window.payoffChartInstance.destroy();
        }

        const prices = payoffData.prices;
        const payoffs = payoffData.payoffs;
    
        const formattedLabels = prices.map(price => price.toFixed(2)); // Pas de décimales dans les labels
    
        window.payoffChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: formattedLabels,
                datasets: [{
                    label: 'Payoff',
                    data: payoffs,
                    borderColor: '#007bff',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.1
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Prix du sous-jacent'
                        },
                        grid: {
                            display: true,
                            color: '#e0e0e0'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Payoff'
                        },
                        grid: {
                            display: true,
                            color: '#e0e0e0'
                        }
                    }
                }
            }
        });
    }
    function updateGreeksDisplay(greeks) {
        const greekTable = document.getElementById("greeks-table");
        const fields = ['delta', 'gamma', 'vega', 'theta', 'rho'];
    
        if (!greeks || typeof greeks !== 'object') {
            console.error("Grecs non valides :", greeks);
            greekTable.style.display = 'none';
            return;
        }
    
        fields.forEach(field => {
            const cell = document.getElementById(field);
            if (cell && greeks[field] !== undefined) {
                cell.textContent = parseFloat(greeks[field]).toFixed(4);
            } else if (cell) {
                cell.textContent = "-";
            }
        });
    
        greekTable.style.display = "table";  // Affiche la table si tout est ok
    }
    // Gérer l'événement de soumission du formulaire
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        spinner.style.display = 'block';

        const formData = new FormData(this);
        const queryString = new URLSearchParams(formData).toString();

        fetch('/calculate_participation_products?' + queryString)
            .then(response => response.json())
            .then(data => {
                document.getElementById("strategy-result-container").style.display = "block";
                document.getElementById("greeks-table").style.display = "table";

                spinner.style.display = 'none';
                resultPrice.textContent = `Price: ${data.price} USD`;

                updateGreeksDisplay(data.greeks);

                if (data.payoff_data && data.payoff_data.prices && data.payoff_data.payoffs) {
                    console.log("Données de payoff:", data.payoff_data);
                    renderPayoffChart(data.payoff_data);
                } else {
                    console.warn("Données de payoff manquantes.");
                }
            })
            .catch(err => {
                spinner.style.display = 'none';
                console.error("Erreur requête:", err);
            });
    });

    // Gérer les changements de stratégie

    tickerSelect.addEventListener("change", fetchTickerPrice);
    fetchTickerPrice();
});
