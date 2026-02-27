
from .core import relay_call

def get_temperature(city: str) -> int:
    response = relay_call("weather", {"city": city})
    return response["temperature"]
