
from genlayer import IntelligentContract
from genlayer_external.weather import get_temperature

class WeatherInsurance(IntelligentContract):

    def __init__(self, threshold: int):
        self.threshold = threshold
        self.paid = False

    def check_and_trigger(self):
        temp = get_temperature("London")

        if temp > self.threshold:
            self.paid = True
