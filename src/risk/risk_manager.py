from typing import Dict, Any
from loguru import logger

class RiskManager:
    """
    Handles pre-trade risk compliance and drawdown tracking.
    """
    
    def __init__(self, max_pos_size: float = 0.2, max_leverage: float = 1.0, max_drawdown: float = 0.1):
        self.max_pos_size = max_pos_size 
        self.max_leverage = max_leverage
        self.max_drawdown = max_drawdown
        self.current_drawdown = 0.0

    def check_trade(self, symbol: str, quantity: float, price: float, total_capital: float, current_positions: Dict[str, float]) -> bool:
        """
        Perform pre-trade risk checks.
        Returns True if trade is approved.
        """
        trade_value = abs(quantity) * price
        
        # 1. Max position size check
        if trade_value > (total_capital * self.max_pos_size):
            logger.warning(f"Risk Check Failed: Position size for {symbol} ({trade_value}) exceeds limit ({total_capital * self.max_pos_size})")
            return False
            
        # 2. Leverage check
        current_exposure = sum(abs(q) * price for s, q in current_positions.items()) # price here should be current spot
        if (current_exposure + trade_value) > (total_capital * self.max_leverage):
            logger.warning(f"Risk Check Failed: Total exposure exceeds leverage limit")
            return False
            
        # 3. Drawdown check (placeholder for more complex logic)
        if self.current_drawdown > self.max_drawdown:
            logger.warning(f"Risk Check Failed: System-wide drawdown limit reached")
            return False
            
        return True

    def update_metrics(self, equity_curve: list):
        # Update current drawdown based on equity curve
        if not equity_curve:
            return
        
        peak = max([e['Equity'] for e in equity_curve])
        current = equity_curve[-1]['Equity']
        self.current_drawdown = (peak - current) / peak if peak > 0 else 0
