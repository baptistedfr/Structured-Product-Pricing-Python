document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("strategy-form");
    const strategyTypeRadios = document.getElementsByName("strategy_type");
    const strikeFieldsContainer = document.getElementById("strike-fields-container");
    const tickerSelect = document.getElementById("ticker");
    const tickerPriceInput = document.getElementById("ticker-price");
    const resultPrice = document.getElementById("strategy-price");
    const payoffCanvas = document.getElementById("payoffChart");
    const spinner = document.getElementById("loading-spinner");
    const maturityCalendarInput = document.getElementById("maturity_calendar");
    const labelMaturityCalendar = document.getElementById("label-maturity-calendar");

    const maturityInput = document.getElementById("maturity");
    const today = new Date();
    const nextYear = new Date(today.setFullYear(today.getFullYear() + 1));
    const formattedDate = nextYear.toISOString().split('T')[0];
    // Définir la date dans le champ input
    maturityInput.value = formattedDate;
    
    // Fonction pour afficher/mettre à jour les champs de strike dynamiquement
    function displayMultipleStrikes(numberOfStrikes) {
        strikeFieldsContainer.innerHTML = ""; // Réinitialiser les champs de strike

        for (let i = 0; i < numberOfStrikes; i++) {
            const strikeInput = document.createElement('div');
            strikeInput.classList.add('row', 'mb-3');
            strikeInput.innerHTML = `
                <label for="strike${i}" class="form-label">Strike ${i + 1}</label>
                <input type="number" class="form-control" id="strike${i}" name="strike${i}" value="100" required>
            `;
            strikeFieldsContainer.appendChild(strikeInput);
        }
    }

    // Fonction pour gérer les événements de sélection des stratégies
    function toggleFields() {
        const selectedStrategyType = document.querySelector("input[name='strategy_type']:checked")?.value;
        console.log(selectedStrategyType)
        if (!selectedStrategyType) return;

        // Détermine combien de strikes sont nécessaires en fonction de la stratégie
        let numberOfStrikes = 1; // Par défaut, une seule strike
        switch (selectedStrategyType) {
            case "strangle":
                numberOfStrikes = 2;
                break;
            case "bull_spread":
                numberOfStrikes = 2;
                break;
            case "bear_spread":
                numberOfStrikes = 2;
                break;
            case "collar_spread":
                numberOfStrikes = 2;
                break;
            case "butterfly_spread":
                numberOfStrikes = 3;
                break;
            case "condor_spread":
                numberOfStrikes = 4;
                break;
            default:
                numberOfStrikes = 1; // Straddle et autres
        }
        if (selectedStrategyType == "calendar_spread") {
            maturityCalendarInput.style.display = "block";  // Afficher l'input
            labelMaturityCalendar.style.display = "block";  // Afficher l'étiquette
        } else {
            maturityCalendarInput.style.display = "none";  // Masquer l'input
            labelMaturityCalendar.style.display = "none";  // Masquer l'étiquette
        }

        // Mise à jour de l'affichage des champs de strike
        displayMultipleStrikes(numberOfStrikes);
    }

    // Fonction pour récupérer le prix du ticker
    function fetchTickerPrice() {
        fetch(`/get_ticker_price?ticker=${tickerSelect.value}`)
            .then(response => response.json())
            .then(data => tickerPriceInput.value = data.ticker_price)
            .catch(err => console.error("Erreur récupération ticker:", err));
    }

    // Fonction pour rendre le graphique du payoff
    function renderPayoffChartStrategy(payoffData) {
        const ctx = document.getElementById('payoffChartStrategy').getContext('2d');
    
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

        fetch('/calculate_price_strategy?' + queryString)
            .then(response => response.json())
            .then(data => {
                document.getElementById("strategy-result-container").style.display = "block";
                document.getElementById("greeks-table").style.display = "table";

                spinner.style.display = 'none';
                resultPrice.textContent = `Price: ${data.price} USD`;

                updateGreeksDisplay(data.greeks);

                if (data.payoff_data && data.payoff_data.prices && data.payoff_data.payoffs) {
                    console.log("Données de payoff:", data.payoff_data);
                    renderPayoffChartStrategy(data.payoff_data);
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
    strategyTypeRadios.forEach(radio => {
        radio.addEventListener("change", toggleFields);
    });
    tickerSelect.addEventListener("change", fetchTickerPrice);

    // Initial setup
    toggleFields(); // Initialisation des champs selon la stratégie par défaut
    fetchTickerPrice();
});
