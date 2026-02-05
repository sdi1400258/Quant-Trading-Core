import pandas as pd
import numpy as np
from typing import List, Dict, Any
from loguru import logger

class Backtester:
    """
    Simplified event-driven backtester.
    Iterates through historical data and executes trades based on signals.
    """
    
    def __init__(self, initial_capital: float = 100000.0, commission: float = 0.001, slippage: float = 0.0005):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.positions = {} # symbol -> quantity
        self.entry_prices = {} # symbol -> entry price
        self.session_highs = {} # symbol -> highest price since entry
        self.trades = []
        self.equity_curve = []

    def run(self, data: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Iterate through timestamps to simulate trade execution.
        """
        logger.info("Starting backtest...")
        
        data = data.reset_index() if 'Date' not in data.columns else data
        signals = signals.reset_index() if 'Date' not in signals.columns else signals
        
        required = ['Date', 'Symbol', 'Target_Position']
        for col in required:
            if col not in signals.columns:
                logger.error(f"Required column missing: {col}")
                raise KeyError(f"Missing column {col} in signals")

        df = pd.merge(data, signals[['Date', 'Symbol', 'Target_Position']], on=['Date', 'Symbol'], how='left')
        df = df.sort_values(['Date', 'Symbol'])
        
        last_prices = {}

        for timestamp, group in df.groupby('Date', sort=True):
            # Update valuations with the latest closing prices
            for _, row in group.iterrows():
                last_prices[row['Symbol']] = row['Close']
            
            pre_trade_equity = self.capital
            for sym, pos in self.positions.items():
                pre_trade_equity += (pos * last_prices.get(sym, 0.0))

            # Normalize weights if they exceed unity
            total_target_weight = group['Target_Position'].sum()
            if total_target_weight > 1.0:
                logger.warning(f"Target weights ({total_target_weight}) exceed capacity on {timestamp}. Downscaling...")
                group['Target_Position'] = group['Target_Position'] / total_target_weight

            for index, row in group.iterrows():
                symbol = row['Symbol']
                price = row['Close']
                target_weight = row['Target_Position']
                
                # Calculate target shares from total portfolio equity
                target_qty = (pre_trade_equity * target_weight) / price if abs(target_weight) > 1e-6 else 0.0
                current_qty = self.positions.get(symbol, 0.0)
                
                # Check for stop triggers
                stop_triggered = False
                if abs(current_qty) > 1e-6:
                    entry_price = self.entry_prices.get(symbol, price)
                    session_high = self.session_highs.get(symbol, price)
                    
                    if price > session_high:
                        self.session_highs[symbol] = price
                        session_high = price
                    
                    # 2% stop-loss from entry
                    stop_loss_pct = 0.02
                    if price < entry_price * (1 - stop_loss_pct):
                        logger.warning(f"Stop-loss hit for {symbol} at {price} (Entry: {entry_price})")
                        stop_triggered = True
                        target_qty = 0
                    
                    # 5% trailing stop from peak
                    trailing_stop_pct = 0.05
                    if price < session_high * (1 - trailing_stop_pct):
                        logger.warning(f"Trailing stop hit for {symbol} at {price} (High: {session_high})")
                        stop_triggered = True
                        target_qty = 0

                # Evaluate if a trade is necessary
                should_trade = False
                if stop_triggered:
                    should_trade = True
                elif abs(target_weight) > 1e-6 and abs(current_qty) < 1e-6:
                    should_trade = True
                elif abs(target_weight) < 1e-6 and abs(current_qty) > 1e-6:
                    should_trade = True
                elif (target_weight > 1e-6 and current_qty < -1e-6) or (target_weight < -1e-6 and current_qty > 1e-6):
                    should_trade = True
                
                if should_trade:
                    # Account for slippage (buy higher, sell lower)
                    execution_price = price * (1 + self.slippage) if target_qty > current_qty else price * (1 - self.slippage)
                    
                    trade_qty = target_qty - current_qty
                    cost = abs(trade_qty) * execution_price
                    comm_cost = cost * self.commission
                    
                    self.capital -= (trade_qty * execution_price + comm_cost)
                    self.positions[symbol] = target_qty
                    
                    if abs(target_qty) > 1e-6:
                        self.entry_prices[symbol] = execution_price
                        self.session_highs[symbol] = execution_price
                    else:
                        self.entry_prices.pop(symbol, None)
                        self.session_highs.pop(symbol, None)
                    
                    self.trades.append({
                        'Date': timestamp,
                        'Symbol': symbol,
                        'Qty': trade_qty,
                        'Price': execution_price,
                        'Cost': cost,
                        'Commission': comm_cost
                    })

            # Calculate end-of-day equity
            post_trade_equity = self.capital
            for sym, pos in self.positions.items():
                post_trade_equity += (pos * last_prices.get(sym, 0.0))
            
            self.equity_curve.append({'Date': timestamp, 'Equity': post_trade_equity})

        logger.info("Backtest completed.")
        return pd.DataFrame(self.equity_curve)

    def get_metrics(self) -> Dict[str, float]:
        df_equity = pd.DataFrame(self.equity_curve)
        if df_equity.empty:
            return {}
            
        returns = df_equity['Equity'].pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        total_return = (df_equity['Equity'].iloc[-1] / self.initial_capital) - 1
        
        return {
            "Total Return": total_return,
            "Sharpe Ratio": sharpe,
            "Final Capital": df_equity['Equity'].iloc[-1]
        }
