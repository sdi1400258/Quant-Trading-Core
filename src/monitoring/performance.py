import pandas as pd
import matplotlib.pyplot as plt
import os
from loguru import logger

class PerformanceMonitor:
    """
    Calculate and persist portfolio metrics.
    """
    
    def __init__(self, output_dir: str = "monitoring"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_report(self, equity_curve: pd.DataFrame, trades: list):
        """
        Export equity visualization and trade data.
        """
        logger.info("Generating performance report...")
        
        # Save equity curve
        plt.figure(figsize=(12, 6))
        plt.plot(equity_curve['Date'], equity_curve['Equity'])
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Total Value')
        plt.grid(True)
        plt.savefig(os.path.join(self.output_dir, "equity_curve.png"))
        plt.close()
        
        # Save equity curve to CSV for the dashboard
        equity_curve.to_csv(os.path.join(self.output_dir, "equity_curve.csv"), index=False)
        
        # Save trades to CSV
        df_trades = pd.DataFrame(trades)
        df_trades.to_csv(os.path.join(self.output_dir, "trade_audit_trail.csv"), index=False)
        
        # Calculate summary metrics
        total_return = (equity_curve['Equity'].iloc[-1] / equity_curve['Equity'].iloc[0]) - 1
        logger.info(f"Report Generated: Total Return = {total_return:.2%}")
        
        return {
            "Total Return": total_return,
            "Trade Count": len(trades),
            "Final Equity": equity_curve['Equity'].iloc[-1]
        }
