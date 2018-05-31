import template from './backtest.html';

const backtestComponent = {
  template,
  controller: class backtestComponent {
    constructor(tradingSessionService, $filter) {
      this.tradingSessionService = tradingSessionService;
      this.$filter = $filter;
    }

    $onInit() {
      /*
        exchange data
        getMarket = {
          exchange: {
            name: 'exchange',
            timeframes: {"1m": "1m", ...},
            symbols:  [...]
          },
          exchanges: [...],
          algorithms: {
            core.strategy: [...],
            core.risk_manager: [...],
          }
        }
      */
      this.marketData = {};
      this.tradingSessionService.getMarket().then((market) => {
        this.marketData = market.data;
        // this.marketData.exchange.symbols = this.$filter('symbolsFilter')(
        // this.marketData.exchange.symbols);
      });
      this.sessionStarted = false;
      console.log(this.onSessionStart);
    }
    // TODO: set sessionStarted to true
    onSessionStart() {

    }
  },
};

export default backtestComponent;
