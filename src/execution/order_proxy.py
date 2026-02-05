import time
import uuid
from loguru import logger

class OrderProxy:
    """
    Simulation bridge between Python strategy and C++ OMS.
    In production, this would use IPC mechanisms like ZeroMQ or shared memory.
    """
    
    def __init__(self):
        self.order_history = {}

    def send_order(self, symbol: str, side: str, qty: int, price: float) -> str:
        order_id = str(uuid.uuid4())
        logger.info(f"Submitting order to OMS: {order_id} | {side} {qty} {symbol} @ {price}")
        
        # Simulated IPC latency
        # time.sleep(0.001) 
        
        self.order_history[order_id] = {
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'price': price,
            'status': 'SUBMITTED'
        }
        return order_id

    def get_order_status(self, order_id: str) -> str:
        # Simulate the C++ OMS updating the status
        if order_id in self.order_history:
            self.order_history[order_id]['status'] = 'FILLED'
            return 'FILLED'
        return 'UNKNOWN'
