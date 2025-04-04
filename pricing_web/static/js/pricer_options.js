document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("pricing-form");
    const optionTypeRadios = document.getElementsByName("option_type");
    const subtypeSelect = document.getElementById("subtype");
    const tickerSelect = document.getElementById("ticker");
    const tickerPriceInput = document.getElementById("ticker-price");
    const volTypeSelect = document.getElementById("vol_type");
    const constantVolContainer = document.getElementById("constant-vol-container");
    const resultPrice = document.getElementById("option-price");
    const payoffCanvas = document.getElementById("payoff-chart");
    const spinner = document.getElementById("loading-spinner");

    let payoffChart = null;

    const optionsData = {
        vanilla: JSON.parse(form.dataset.vanillaOptions),
        path_dependent: JSON.parse(form.dataset.pathDependentOptions),
        barrier: JSON.parse(form.dataset.barrierOptions),
        binary: JSON.parse(form.dataset.binaryOptions),
    };

    function toggleFields() {
        const selectedOptionType = document.querySelector("input[name='option_type']:checked")?.value;
        if (!selectedOptionType) return;

        const options = optionsData[selectedOptionType];
        populateSubtypes(options);

        document.getElementById("subtype-fields").style.display = "block";
        document.getElementById("barrier-fields").style.display = selectedOptionType === "barrier" ? "block" : "none";
        document.getElementById("coupon-fields").style.display = selectedOptionType === "binary" ? "block" : "none";
    }

    function populateSubtypes(options) {
        subtypeSelect.innerHTML = "";
        options.forEach(opt => {
            const option = document.createElement("option");
            option.value = opt.value;
            option.textContent = opt.label;
            subtypeSelect.appendChild(option);
        });
    }

    function toggleConstantVolInput() {
        constantVolContainer.style.display = volTypeSelect.value === "constant" ? "block" : "none";
    }

    function fetchTickerPrice() {
        fetch(`/get_ticker_price?ticker=${tickerSelect.value}`)
            .then(response => response.json())
            .then(data => tickerPriceInput.value = data.ticker_price)
            .catch(err => console.error("Erreur récupération ticker:", err));
    }

    function renderPayoffChart(payoffData) {
        const ctx = document.getElementById('payoffChart').getContext('2d');
    
        // Si un graphique existe déjà, on le détruit pour en recréer un propre
        if (window.payoffChartInstance) {
            window.payoffChartInstance.destroy();
        }
    
        // Utiliser les prix originaux pour les données
        const prices = payoffData.prices;
        const payoffs = payoffData.payoffs;
    
        // Formater les prix uniquement pour les labels (en les arrondissant sans décimales)
        const formattedLabels = prices.map(price => price.toFixed(2)); // Pas de décimales dans les labels
    
        window.payoffChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: formattedLabels,  // Afficher les prix arrondis pour les labels
                datasets: [{
                    label: 'Payoff',
                    data: payoffs,  // Garder les payoffs d'origine
                    borderColor: '#007bff',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    pointRadius: 0, // Supprime les petits points
                    tension: 0.1    // Ligne légèrement courbée pour plus de lisibilité
                }]
            },
            options: {
                responsive: false,  // Taille contrôlée manuellement
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
                        },
                        ticks: {
                            callback: function(value) {
                                return value;  // Retourner la valeur sans décimales dans les labels
                            }
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


    form.addEventListener("submit", function (event) {
        event.preventDefault();
        spinner.style.display = 'block';

        const formData = new FormData(this);
        const queryString = new URLSearchParams(formData).toString();

        fetch('/calculate_price_options?' + queryString)
            .then(response => response.json())
            .then(data => {
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

    // Initialisation
    optionTypeRadios.forEach(radio => radio.addEventListener("change", toggleFields));
    volTypeSelect.addEventListener("change", toggleConstantVolInput);
    tickerSelect.addEventListener("change", fetchTickerPrice);

    toggleFields();
    toggleConstantVolInput();
    fetchTickerPrice();
});
