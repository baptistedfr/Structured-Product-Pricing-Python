document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("pricing-form");
    const resultPrice = document.getElementById("swap-price");
    const priceContainer = document.getElementById("price-container");
    const rateContainer = document.getElementById("rate-container");
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

    var achatDate = new Date(today.setFullYear(today.getFullYear() - 2));
    var formattedAchat = achatDate.toISOString().split('T')[0];

    achatInput.value = formattedAchat;

    function toggleManualCouponInput() {
        console.log("hr")
        const selectedMode = Array.from(pricingModeRadios).find(radio => radio.checked)?.value;
        if (selectedMode === "pricing") {
            priceContainer.style.display = "none";
            rateContainer.style.display = "block";
            calculateBtn.textContent = "Calculer le Prix";
        } else {
            priceContainer.style.display = "block";
            rateContainer.style.display = "none";
            calculateBtn.textContent = "Calculer le taux fixe";
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
            ? `/calculate_swap_price?${queryString}`
            : `/calculate_swap_rate?${queryString}`;

        fetch(url + queryString)
            .then(response => response.json())
            .then(data => {
                document.getElementById("swap-result-container").style.display = "block";

                spinner.style.display = 'none';
                resultPrice.textContent = isPricingMode
                ? `Prix : ${data.price} €`
                : `Taux Fixe : ${data.rate} %`;
                
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
