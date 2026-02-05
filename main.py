import sys
import os
from datetime import datetime
from loguru import logger

# Add src to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.ingestion.yf_loader import YFinanceLoader
from src.processing.features import generate_features
from src.strategy.ma_cross import MovingAverageCross
from src.backtesting.engine import Backtester
from src.risk.risk_manager import RiskManager
from src.execution.order_proxy import OrderProxy
from src.monitoring.performance import PerformanceMonitor

def main():
    logger.add("logs/trading_system.log", rotation="1 MB")
    logger.info("Initializing Full Trading Pipeline...")

    # Data Ingestion
    loader = YFinanceLoader(raw_data_dir="data/raw", processed_data_dir="data/processed")
    symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "AMD", "META"] 
    start_date = "2025-01-01"
    end_date = "2026-02-01" 
    
    df_raw = loader.run_pipeline(symbols, start_date, end_date)
    
    # Feature Engineering
    logger.info("Generating features...")
    df_features = generate_features(df_raw)
    
    # Strategy Layer
    logger.info("Executing strategy...")
    strategy = MovingAverageCross(fast_window=10, slow_window=30)
    df_signals = strategy.generate_signals(df_features)
    
    # Backtesting
    logger.info("Running backtest...")
    # Simulation parameters: 10bps slippage, 5bps commission
    bt = Backtester(initial_capital=100000, commission=0.0005, slippage=0.0010)
    equity_curve = bt.run(df_features, df_signals)
    
    # Risk Management
    risk = RiskManager(max_pos_size=0.3)
    risk.update_metrics(bt.equity_curve)
    
    # Execution (Order routing simulation)
    proxy = OrderProxy()
    last_row = df_signals.iloc[-1]
    if last_row['Signal'] != 0:
        side = 'BUY' if last_row['Signal'] > 0 else 'SELL'
        order_id = proxy.send_order(last_row['Symbol'], side, 10, last_row['Close'])
        proxy.get_order_status(order_id)
        
    # Monitoring & Evaluation
    monitor = PerformanceMonitor(output_dir="monitoring")
    metrics = monitor.generate_report(equity_curve, bt.trades)
    
    print("\n" + "="*30)
    print("      PIPELINE RESULTS      ")
    print("="*30)
    for k, v in metrics.items():
        print(f"{k}: {v}")
    print("="*30)

if __name__ == "__main__":
    main()
