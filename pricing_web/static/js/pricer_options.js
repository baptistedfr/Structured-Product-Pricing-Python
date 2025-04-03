document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("pricing-form");
    const optionTypeRadios = document.getElementsByName("option_type");
    const subtypeSelect = document.getElementById("subtype");
    const tickerSelect = document.getElementById("ticker");
    const tickerPriceInput = document.getElementById("ticker-price");
    const volTypeSelect = document.getElementById("vol_type");
    const constantVolContainer = document.getElementById("constant-vol-container");
    const resultPrice = document.getElementById("option-price");
    const payoffGraph = document.getElementById("payoff-graph");

    // Récupérer les options dynamiques depuis les attributs data-*
    const optionsData = {
        vanilla: JSON.parse(form.dataset.vanillaOptions),
        path_dependent: JSON.parse(form.dataset.pathDependentOptions),
        barrier: JSON.parse(form.dataset.barrierOptions),
        binary: JSON.parse(form.dataset.binaryOptions),
    };
    console.log(optionsData)
    

    tickerSelect.addEventListener("change", function () {
        fetchTickerPrice(); // Ensuite on récupère le prix
    });
    function toggleFields() {
        let selectedOptionType = document.querySelector("input[name='option_type']:checked")?.value;
        console.log("Option sélectionnée:", selectedOptionType);
        
        if (!selectedOptionType) {
            console.log("Aucune option sélectionnée !");
            return;  // Empêche une erreur si aucune option n'est sélectionnée
        }
    
        const options = optionsData[selectedOptionType];
        
        if (!options) {
            console.log("Aucune donnée trouvée pour cette option.");
            return;
        }
    
        // Affichage de la section des sous-options
        document.getElementById("subtype-fields").style.display = "block"; 
    
        // Vider le select avant d'ajouter les nouvelles options
        populateSubtypes(options);
        
        // Masquer ou afficher la section spécifique en fonction de l'option choisie
        if (selectedOptionType === "barrier") {
            document.getElementById("barrier-fields").style.display = "block";  // Afficher la barrière
        } else {
            document.getElementById("barrier-fields").style.display = "none";   // Masquer la barrière
        }
    
        if (selectedOptionType === "binary") {
            document.getElementById("coupon-fields").style.display = "block";    // Afficher le coupon pour les binaires
        } else {
            document.getElementById("coupon-fields").style.display = "none";     // Masquer le coupon
        }
    }
    
    function populateSubtypes(options) {
        const subtypeSelect = document.getElementById("subtype");
        subtypeSelect.innerHTML = "";  // Vider les anciennes options
    
        if (!options || options.length === 0) {
            console.log("Aucune option à afficher");
            return;  // Empêche une erreur si aucune option n'existe
        }
    
        options.forEach(option => {
            const opt = document.createElement("option");
            opt.value = option.value;
            opt.textContent = option.label;
            subtypeSelect.appendChild(opt);
        });
    }
    function toggleConstantVolInput() {
        constantVolContainer.style.display = volTypeSelect.value === "constant" ? "block" : "none";
    }

    function fetchTickerPrice() {
        fetch(`/get_ticker_price?ticker=${tickerSelect.value}`)
            .then(response => response.json())
            .then(data => tickerPriceInput.value = data.ticker_price)
            .catch(error => console.error("Erreur récupération prix ticker:", error));
        console.log("Ticker sélectionné:", tickerSelect.value);  // Vérifier la valeur sélectionnée
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        document.getElementById('loading-spinner').style.display = 'block';
        let formData = new FormData(this);
        let queryString = new URLSearchParams(formData).toString();
        fetch('http://127.0.0.1:8000/calculate_price_options?' + queryString)
        .then(response => response.json())
        .then(data => {
            document.getElementById('loading-spinner').style.display = 'none';
            console.log(data);
            const priceElement = document.getElementById('option-price');
            priceElement.textContent = `Price: ${data.price} USD`;
            
            document.getElementById('delta').textContent = data.greeks.delta.toFixed(4);
            document.getElementById('gamma').textContent = data.greeks.gamma.toFixed(4);
            document.getElementById('vega').textContent = data.greeks.vega.toFixed(4);
            document.getElementById('theta').textContent = data.greeks.theta.toFixed(4);
            document.getElementById('rho').textContent = data.greeks.rho.toFixed(4);
            
            // Afficher le graphique de payoff, si disponible
            const graphElement = document.getElementById('payoff-graph');
            if (data.payoff_graph) {
                graphElement.src = data.payoff_graph;  // Met à jour l'élément image avec l'URL du graphique
                graphElement.style.display = 'block';  // Affiche l'image
            } else {
                console.error('Erreur : Le graphique n\'a pas été généré correctement.');
            }
        })
        .catch(error => console.error('Erreur requête AJAX:', error));
    });

    optionTypeRadios.forEach(radio => radio.addEventListener("change", toggleFields));
    volTypeSelect.addEventListener("change", toggleConstantVolInput);
    tickerSelect.addEventListener("change", fetchTickerPrice);

    // Initialisation au chargement de la page
    toggleFields();
    toggleConstantVolInput();
    fetchTickerPrice();
});