document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("pricing-form");
    const resultPrice = document.getElementById("bond-price");
    const priceContainer = document.getElementById("price-container");
    const ytmContainer = document.getElementById("ytm-container");
    const spinner = document.getElementById("loading-spinner");
    const pricingModeRadios = document.getElementsByName("pricing_mode");
    const calculateBtn = document.getElementById("calculate-btn");
    const EmissionInput = document.getElementById("emission");
    const maturityInput = document.getElementById("maturity");
    const achatInput = document.getElementById("achat");

    const today = new Date();
    var nextYear = new Date(today.setFullYear(today.getFullYear() + 3));
    var formattedDate = nextYear.toISOString().split('T')[0];
    // Définir la date dans le champ input
    maturityInput.value = formattedDate;

    const todayDate = new Date().toISOString().split('T')[0];
    EmissionInput.value = todayDate;
    achatInput.value = todayDate;

    function toggleManualCouponInput() {
        const selectedMode = Array.from(pricingModeRadios).find(radio => radio.checked)?.value;
        if (selectedMode === "pricing") {
            priceContainer.style.display = "none";
            ytmContainer.style.display = "block";
            calculateBtn.textContent = "Calculer le Prix";
        } else {
            priceContainer.style.display = "block";
            ytmContainer.style.display = "none";
            calculateBtn.textContent = "Calculer le Coupon";
        }
    }

    
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        spinner.style.display = 'block';

        const formData = new FormData(this);
        const queryString = new URLSearchParams(formData).toString();
        const selectedMode = Array.from(pricingModeRadios).find(radio => radio.checked)?.value;
        const isPricingMode = selectedMode === "pricing";
        const url = isPricingMode
            ? `/calculate_bond_price?${queryString}`
            : `/calculate_bond_coupon?${queryString}`;

        fetch(url + queryString)
            .then(response => response.json())
            .then(data => {
                document.getElementById("bond-result-container").style.display = "block";

                spinner.style.display = 'none';
                resultPrice.textContent = isPricingMode
                ? `Prix : ${data.price} €`
                : `YTM : ${data.ytm} %`;
                
            })
            .catch(err => {
                spinner.style.display = 'none';
                console.error("Erreur requête:", err);
            });
    });

    
    pricingModeRadios.forEach(radio => {
        radio.addEventListener("change", toggleManualCouponInput);
    });
    toggleManualCouponInput();

});
