document.addEventListener('DOMContentLoaded', function () {
    const optionTypeRadios = document.getElementsByName('option_type');
    const subtypeFields = document.getElementById('subtype-fields');
    const subtypeSelect = document.getElementById('subtype');
    const tickerSelect = document.getElementById('ticker');
    const tickerPriceInput = document.getElementById('ticker-price');
    const volTypeSelect = document.getElementById('vol_type');
    const constantVolContainer = document.getElementById('constant-vol-container');
    const binaryFields = document.getElementById('binary-fields');
    const barrierFields = document.getElementById('barrier-fields');

    // Fonction pour afficher/masquer les champs dynamiques
    function toggleFields() {
        let selectedOptionType = '';
        optionTypeRadios.forEach(radio => {
            if (radio.checked) {
                selectedOptionType = radio.value;
            }
        });

        // Réinitialiser les champs dynamiques
        subtypeFields.style.display = 'none';
        binaryFields.style.display = 'none';
        barrierFields.style.display = 'none';

        // Afficher les champs dynamiques en fonction du type d'option
        if (selectedOptionType === 'vanilla') {
            populateSubtypes(JSON.parse(document.getElementById('options-form').dataset.vanillaOptions));
            subtypeFields.style.display = 'block';
        } else if (selectedOptionType === 'path_dependent') {
            populateSubtypes(JSON.parse(document.getElementById('options-form').dataset.pathDependentOptions));
            subtypeFields.style.display = 'block';
        } else if (selectedOptionType === 'binary') {
            binaryFields.style.display = 'block';
            populateSubtypes(JSON.parse(document.getElementById('options-form').dataset.binaryOptions));
        } else if (selectedOptionType === 'barrier') {
            barrierFields.style.display = 'block';
            populateSubtypes(JSON.parse(document.getElementById('options-form').dataset.barrierOptions));
        }
    }

    // Fonction pour remplir les sous-options
    function populateSubtypes(options) {
        subtypeSelect.innerHTML = '';
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option.value;
            opt.textContent = option.label;
            subtypeSelect.appendChild(opt);
        });
    }

    // Fonction pour afficher/masquer le champ de volatilité constante
    function toggleConstantVolInput() {
        if (volTypeSelect.value === 'constant') {
            constantVolContainer.style.display = 'block';
        } else {
            constantVolContainer.style.display = 'none';
        }
    }

    // Fonction pour récupérer et afficher le prix du ticker
    function fetchTickerPrice() {
        const selectedTicker = tickerSelect.value;
        fetch(`/get_ticker_price?ticker=${selectedTicker}`)
            .then(response => response.json())
            .then(data => {
                tickerPriceInput.value = data.ticker_price;
            })
            .catch(error => console.error('Erreur lors de la récupération du prix du ticker:', error));
    }

    // Écouteurs d'événements
    optionTypeRadios.forEach(radio => radio.addEventListener('change', toggleFields));
    volTypeSelect.addEventListener('change', toggleConstantVolInput);
    tickerSelect.addEventListener('change', fetchTickerPrice);

    // Initialisation
    toggleFields();
    toggleConstantVolInput();
    fetchTickerPrice();
});