from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional, Any
from pathlib import Path

class BaseDataLoader(ABC):
    """
    Abstract interface for data loaders.
    Handles fetching, cleaning, and persisting market data.
    """
    
    def __init__(self, raw_data_dir: str, processed_data_dir: str):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch_data(self, symbols: List[str], start_date: str, end_date: str, interval: str = "1d") -> Any:
        """Fetch raw data from the source."""
        pass

    @abstractmethod
    def clean_data(self, raw_data: Any) -> pd.DataFrame:
        """Clean and normalize the raw data."""
        pass

    @abstractmethod
    def store_data(self, df: pd.DataFrame, filename: str, format: str = "parquet"):
        """Store processed data in a specified format."""
        pass

    def run_pipeline(self, symbols: List[str], start_date: str, end_date: str, interval: str = "1d"):
        """Orchestrate the ingestion pipeline."""
        raw_data = self.fetch_data(symbols, start_date, end_date, interval)
        clean_df = self.clean_data(raw_data)
        self.store_data(clean_df, f"market_data_{start_date}_{end_date}.parquet")
        return clean_df
