import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from . import AbstractVolatilitySurface
from kernel.market_data import RateCurve
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm


class LocalVolatilitySurface(AbstractVolatilitySurface):
    """
    Defines the Local Volatility Surface based on Dupire's formula to compute the local volatility 
    from market option prices and an implied volatility surface.

    The local volatility model assumes that the dynamics of the underlying asset follow a stochastic 
    process with a volatility that is both time- and state-dependent. This model is particularly useful 
    for pricing exotic derivatives and understanding the behavior of implied volatility surfaces.

    The local volatility is derived using Dupire's formula:
        σ_local^2(K, T) = (∂C/∂T + r * K * ∂C/∂K) / (0.5 * K^2 * ∂²C/∂K²)
    where:
        - C is the call price
        - K is the strike price
        - T is the maturity
        - r is the risk-free rate

    This class provides methods to compute local volatility, visualize volatility smiles, and display 
    the local volatility surface in 3D.

    Attributes:
        option_data (pd.DataFrame): Market option data containing columns such as 'Strike', 'Spot', 
                                    'Maturity', and 'Implied Volatility'.
        rate_curve (RateCurve): Object providing the risk-free rate curve (must have a `get_rate` method).
        svi_surface (SVIVolatilitySurface): Calibrated implied volatility surface (must have `get_volatility` 
                                            and `interpolators` attributes).
        spot (float): Spot price of the underlying asset.
    """

    def __init__(self, option_data: pd.DataFrame, rate_curve: RateCurve, svi_surface: 'SVIVolatilitySurface'): # type: ignore
        """
        Initializes the LocalSurfaceVolatility class with market option data, a rate curve, and an SVI surface.

        Parameters:
            option_data (pd.DataFrame): Market option data containing columns such as 'Strike', 'Spot', 'Maturity', and 'Implied Volatility'.
            rate_curve (RateCurve): Object providing the risk-free rate curve.
            svi_surface (SVIVolatilitySurface): Calibrated implied volatility surface.
        """        
        # Ensure that the SVI surface is calibrated
        if not svi_surface.is_calibrated:
            svi_surface.calibrate_surface()

        self.option_data = option_data
        self.rate_curve = rate_curve
        self.svi_surface = svi_surface
        self.spot = svi_surface.spot
    
    def calibrate_surface(self):
        """
        This method is a placeholder and does not perform any operations in this implementation as the local volatility has no calibration step (no parameters to fit).
        """
        pass

    def _option_price(self, strike: float, maturity: float) -> float:
        """
        Compute the price of a call option using the Black-Scholes formula.

        Parameters:
            strike (float): Strike price of the option.
            maturity (float): Maturity of the option in years.

        Returns:
            float: Price of the call option.
        """
        S = self.spot
        sigma = self.svi_surface.get_volatility(strike, maturity)
        r = self.rate_curve.get_rate(maturity) / 100.0

        d1 = (np.log(S / strike) + (r + 0.5 * sigma ** 2) * maturity) / (sigma * np.sqrt(maturity))
        d2 = d1 - sigma * np.sqrt(maturity)

        return S * norm.cdf(d1) - strike * np.exp(-r * maturity) * norm.cdf(d2)

    def _finite_difference(self, func: callable, x: float, order: int =1, delta: float = 0.01):
        """
        Generic finite difference method to compute the derivative of a function.
        Can compute first and second derivatives.

        Parameters:
            func (callable): Function to differentiate.
            x (float): Point at which to evaluate the derivative.
            order (int): Order of the derivative (1 or 2).
            delta (float): Small perturbation value for finite difference.

        Returns:
            float: Approximated derivative at point x.
        """
        eps = x * 0.01 if x * 0.01 > 1e-4 else 1e-4

        if order == 1:
            return (func(x + eps) - func(x - eps)) / (2 * eps)
        elif order == 2:
            return (func(x + eps) - 2 * func(x) + func(x - eps)) / (eps ** 2)
        else:
            raise ValueError("Derivative order must be 1 or 2.")

    def _compute_derivatives(self, strike: float, maturity: float):
        """
        Compute the finite difference derivatives needed for Dupire's formula.

        Parameters:
            strike (float): Strike price of the option.
            maturity (float): Maturity of the option in years.

        Returns:
            tuple: Tuple containing the first derivative with respect to strike, 
                   second derivative with respect to strike, and first derivative with respect to maturity.
        """
        f_K = lambda K: self._option_price(K, maturity)
        f_T = lambda T: self._option_price(strike, T)
        
        dC_dK = self._finite_difference(f_K, strike, order=1)
        d2C_dK2 = self._finite_difference(f_K, strike, order=2)
        dC_dT = self._finite_difference(f_T, maturity, order=1)
        
        return dC_dK, d2C_dK2, dC_dT

    def get_volatility(self, strike: float, maturity: float) -> float:
        """
        Compute the local volatility using Dupire's formula for a given strike and maturity.

        Parameters:
            strike (float): Strike price of the option.
            maturity (float): Maturity of the option in years.

        Returns:
            float: Local volatility for the given strike and maturity.
        """
        dC_dK, d2C_dK2, dC_dT = self._compute_derivatives(strike, maturity)
        r = self.rate_curve.get_rate(maturity) / 100.0
        
        numerator = dC_dT + r * strike * dC_dK
        denominator = 0.5 * strike**2 * d2C_dK2

        return np.sqrt(max(numerator / denominator, 0))

    def display_smiles(self) -> None:
        """
        Displays the local volatility smiles for all maturities in the option data.
        Each subplot corresponds to a specific maturity and shows both market data and the interpolated smile.
        """
        unique_maturities = np.sort(self.option_data["Maturity"].unique())
        num_maturities = len(unique_maturities)
        cols = 4
        rows = (num_maturities + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
        axes = axes.flatten()

        strikes_range = np.linspace(self.spot / 2, self.spot * 2, 500)

        for i, T in enumerate(unique_maturities):
            local_vols = []
            for K in strikes_range:
                try:
                    lv = self.get_volatility(K, T)
                except Exception:
                    lv = np.nan
                local_vols.append(lv * 100)  # en pourcentage

            ax = axes[i]
            # Pour comparaison, on trace aussi la smile implicite obtenue par SVI
            svi_vols = [self.svi_surface.get_volatility(K, T) * 100 for K in strikes_range]
            ax.plot((strikes_range / self.spot) * 100, local_vols, label="Vol locale", color="green")
            ax.plot((strikes_range / self.spot) * 100, svi_vols, label="Vol implicite SVI", color="orange", linestyle="--")
            ax.set_title(f"Maturité : {int(T * 252)} jours", fontsize=12, fontweight="bold")
            ax.set_xlabel("Moneyness (% ATM)", fontsize=10)
            ax.set_ylabel("Volatilité (%)", fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, linestyle="--", alpha=0.7)

        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        plt.tight_layout()
        plt.show()

    def display_surface(self) -> None:
        """
        Display the local volatility surface in 3D.
        """
        strikes = np.linspace(self.spot / 2, self.spot * 2, 50)
        maturities = np.linspace(self.option_data["Maturity"].min(), self.option_data["Maturity"].max(), 50)
        local_surface = np.zeros((len(strikes), len(maturities)))

        for i, K in enumerate(strikes):
            for j, T in enumerate(maturities):
                try:
                    local_surface[i, j] = self.get_volatility(K, T) * 100
                except Exception:
                    local_surface[i, j] = np.nan

        X, Y = np.meshgrid(maturities * 252, (strikes / self.spot) * 100)
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(X, Y, local_surface, cmap="viridis", edgecolor="k", alpha=0.8)
        
        market_strikes = (self.option_data["Strike"] / self.spot) * 100
        market_maturities = self.option_data["Maturity"] * 252
        market_vols = self.option_data["Implied Volatility"]
        ax.scatter(market_maturities, market_strikes, market_vols, color="red", label="Options de marché", s=20)

        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
        cbar.set_label("Volatilité locale (%)", fontsize=12)
        ax.set_xlabel("Maturité (jours)", fontsize=12, labelpad=10)
        ax.set_ylabel("Moneyness (% ATM)", fontsize=12, labelpad=10)
        ax.set_zlabel("Volatilité (%)", fontsize=12, labelpad=10)
        ax.set_title("Surface de Volatilité Locale (Dupire)", fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()

    def display_price_surface(self) -> None:
        """
        Display the price surface of calls in 3D.
        """
        strikes = np.linspace(self.spot / 2, self.spot * 2, 50)
        maturities = np.linspace(self.option_data["Maturity"].min(), self.option_data["Maturity"].max(), 50)
        price_surface = np.zeros((len(strikes), len(maturities)))

        for i, K in enumerate(strikes):
            for j, T in enumerate(maturities):
                try:
                    price_surface[i, j] = self.call_price(K, T)
                except Exception:
                    price_surface[i, j] = np.nan

        X, Y = np.meshgrid(maturities * 252, (strikes / self.spot) * 100)
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(X, Y, price_surface, cmap="plasma", edgecolor="k", alpha=0.8)
        
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
        cbar.set_label("Prix du Call", fontsize=12)
        ax.set_xlabel("Maturité (jours)", fontsize=12, labelpad=10)
        ax.set_ylabel("Moneyness (% ATM)", fontsize=12, labelpad=10)
        ax.set_zlabel("Prix du Call", fontsize=12, labelpad=10)
        ax.set_title("Surface des Prix des Options (Black)", fontsize=14, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()
