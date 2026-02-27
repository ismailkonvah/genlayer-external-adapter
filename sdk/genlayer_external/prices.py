
from .core import relay_call

def get_price(symbol: str) -> float:
    response = relay_call("price", {"symbol": symbol})
    return response["price"]
