import yfinance as yf
from dataclasses import dataclass
import pandas as pd
from datetime import datetime


@dataclass
class YahooOption:
    """_summary_
    Generic option data retriever from YahooFinance using option_chain
    Args:
        ticker_name (str) : name of the YahooFinance ticker
        treshold_maturities (float) : % of the closest maturity to filter
        treshold_volume (float) : minimum amount of option traded at a given strike to keep this option in the dataset
        treshold_vol (float) : minimum volatility value to keep this option in the dataset
    """
    ticker_name: str
    treshold_maturities: float = 0
    treshold_volume: float = 0
    treshold_vol: float = 0

    @property
    def ticker(self) -> yf.Ticker:
        return yf.Ticker(self.ticker_name)

    @property
    def maturities(self) -> list[datetime]:
        mat = list(self.ticker.options)
        treshold = int(self.treshold_maturities * len(mat) / 100)
        mat_filtered = mat[treshold:]

        return mat_filtered

    def _retreat_dataset(self, df: pd.DataFrame, maturity: datetime) -> pd.DataFrame:

        df = df[['strike', 'lastPrice', 'volume', 'impliedVolatility']]

        date_maturity = (datetime.strptime(maturity, '%Y-%m-%d') - datetime.now()).days
        df = df.copy()
        df.loc[:, 'maturity'] = date_maturity

        df = df[df['volume'] >= self.treshold_volume]
        df = df[df['impliedVolatility'] >= self.treshold_vol]

        return df

    def get_options(self) -> pd.DataFrame:

        all_calls = pd.DataFrame()
        all_puts = pd.DataFrame()
        for i, mat in enumerate(self.maturities):
            try:
                options = self.ticker.option_chain(self.ticker.options[i])
                calls = options.calls
                puts = options.puts

                calls = self._retreat_dataset(calls, mat)
                puts = self._retreat_dataset(puts, mat)

                all_calls = pd.concat([all_calls, calls])
                all_puts = pd.concat([all_puts, puts])
            except Exception as e:
                print(e)

        all_calls['type'] = 'call'
        all_puts['type'] = 'put'
        all_options = pd.concat([all_calls, all_puts]).fillna(0)

        return all_options


def print_infos(yf_option: YahooOption) -> None:
    options = yf_option.get_options()
    print("-----------------------------------------------------")
    print(f"Ticker selected :  {yf_option.ticker_name}")
    print(f"Last ticker spot : {round(yf_option.ticker.history(period="1d")['Close'].values[-1], 5)}")
    print(f"{len(options)} options downloaded !")
    print(f"Availiable maturities : {yf_option.maturities}")
    print("Option extract :")
    print(options.head(10))
    print("-----------------------------------------------------")