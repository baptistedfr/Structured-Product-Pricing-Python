document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("strategy-form");
    const autocallTypeRadios = document.getElementsByName("autocall_type");
    
    const tickerSelect = document.getElementById("ticker");
    const tickerPriceInput = document.getElementById("ticker-price");
    const resultPrice = document.getElementById("autocall-price");
    const barriereCouponContainter = document.getElementById("barriereCoupon-container");
    const spinner = document.getElementById("loading-spinner");
  

    function toggleBarriereCouponInput() {
        console.log("here")
        const selectedAutocallType = Array.from(autocallTypeRadios).find(radio => radio.checked);
        if (selectedAutocallType) {
            barriereCouponContainter.style.display = selectedAutocallType.value === "phoenix" ? "block" : "none";
        }
    }

    // Fonction pour récupérer le prix du ticker
    function fetchTickerPrice() {
        fetch(`/get_ticker_price?ticker=${tickerSelect.value}`)
            .then(response => response.json())
            .then(data => tickerPriceInput.value = data.ticker_price)
            .catch(err => console.error("Erreur récupération ticker:", err));
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

        fetch('/calculate_autocall_coupon?' + queryString)
            .then(response => response.json())
            .then(data => {
                document.getElementById("autocall-result-container").style.display = "block";
                document.getElementById("greeks-table").style.display = "table";

                spinner.style.display = 'none';
                resultPrice.textContent = `Coupon: ${data.coupon} %`;

                updateGreeksDisplay(data.greeks);
            })
            .catch(err => {
                spinner.style.display = 'none';
                console.error("Erreur requête:", err);
            });
    });

    
    tickerSelect.addEventListener("change", fetchTickerPrice);
    autocallTypeRadios.forEach(radio => {
        radio.addEventListener("change", toggleBarriereCouponInput);
    });
    fetchTickerPrice();
    toggleBarriereCouponInput();
});
