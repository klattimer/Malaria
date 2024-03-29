from Malaria.Plugins import MalariaPlugin
import yfinance as yf

class YFinance(MalariaPlugin):

    def __init__(self, malaria, symbols, keys=None, **kwargs):
        super(YFinance, self).__init__(malaria, **kwargs)
        self.symbols = symbols
        if keys is None: 
            keys = [
                'dayHigh',
                'dayLow',
                'open',
                'lastPrice',
                'previousClose'
            ]
        self.keys = keys

        for symbol in self.symbols:
            ha_topic = '/'.join([
                self.__class__.__name__,
                symbol,
                'lastPrice'
            ])
            self.malaria.register_homeassistant_sensor(
                ha_topic,
                None,
                symbol,
                '',
                'float',
                'mdi:finance'
            )
    
    def update(self):
        data = {}
        for symbol in self.symbols:
            info = yf.Ticker(symbol).fast_info
            data[symbol] = {key: info[key] for key in self.keys if key in info.keys()}
        self.report_data(data, True)