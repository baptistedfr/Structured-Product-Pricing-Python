import pandas as pd
import os

class UnderlyingAsset:
    """
    Represents an underlying asset in the financial market.

    Attributes:
        name (str): Name of the underlying asset
        ticker (str): Ticker of the underlying asset
        isin (str): ISIN code of the underlying asset
        is_index (bool): Boolean indicating if the underlying asset is an index
        last_price (float): Last known price of the underlying asset
    """

    def __init__(self, name: str):
        """
        Initialize an underlying asset.

        Parameters:
            name (str): Name of the underlying asset
        """
        self.name = name

        self.ticker: str= None
        self.isin: str = None
        self.is_index: bool = None
        self.last_price: float = None

    def load_underlying_info(self, file_path: str = 'data/underlying_data.xlsx'):
        """
        Load the price of the underlying asset from an Excel file.

        Parameters:
            file_path (str): Path to the Excel file containing the data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the required columns are missing or the security name is not found
            Exception: For any other errors during file reading or processing
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        df_underlying = pd.read_excel(file_path)

        required_columns = ["Security Label", "Ticker", "ISIN", "Is Index", "Last Price"]
        missing_columns = [col for col in required_columns if col not in df_underlying.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        asset_info = df_underlying[df_underlying["Security Label"] == self.name]
        if asset_info.empty:
            raise ValueError(f"No data found for security name: {self.name}")

        self.ticker = str(asset_info["Ticker"].iloc[0])
        self.isin = str(asset_info["ISIN"].iloc[0])
        self.is_index = bool(asset_info["Is Index"].iloc[0])
        self.last_price = float(asset_info["Last Price"].iloc[0])
