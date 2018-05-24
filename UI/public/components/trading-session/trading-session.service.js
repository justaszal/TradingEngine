export default class tradingSessionService {
  constructor($http, servicesRegistry) {
    this.$http = $http;
    this.servicesRegistry = servicesRegistry;
    this.ohlcvIndexes = {
      open: 0,
      high: 1,
      low: 2,
      close: 3,
      volume: 4,
    };
  }

  startLiveSession() {
    return this.$http({
      method: 'GET',
      url: `http://${this.servicesRegistry.trader}/live_session`,
    });
  }

  getAlgorithms() {
    return this.$http({
      method: 'GET',
      url: `http://${this.servicesRegistry.trader}/algorithms`,
    });
  }

  startBacktestSession() {
    return this.$http({
      method: 'GET',
      url: `http://${this.servicesRegistry.trader}/backtest`,
      cache: true,
    });
  }

  dataframeToCandlesArray(df) {
    const candlesData = {};

    Object.keys(df).forEach((ticker) => {
      candlesData[ticker] = [];

      Object.keys(df[ticker].close).forEach((row) => {
        const timestamp = df[ticker].timestamp[row];
        const open = df[ticker].open[row];
        const high = df[ticker].high[row];
        const low = df[ticker].low[row];
        const close = df[ticker].close[row];
        const volume = df[ticker].volume[row];

        candlesData[ticker].push([
          timestamp,
          open,
          high,
          low,
          close,
          volume,
        ]);
      });
    });

    return candlesData;
  }

  dataframeToCandlesAndVolumeArray(df) {
    const candlesData = {};

    Object.keys(df).forEach((ticker) => {
      candlesData[ticker] = {
        ohlc: [],
        volume: [],
      };

      Object.keys(df[ticker].close).forEach((row) => {
        const timestamp = df[ticker].timestamp[row];
        const open = df[ticker].open[row];
        const high = df[ticker].high[row];
        const low = df[ticker].low[row];
        const close = df[ticker].close[row];
        const volume = df[ticker].volume[row];

        candlesData[ticker].ohlc.push([
          timestamp,
          open,
          high,
          low,
          close,
        ]);

        candlesData[ticker].volume.push([
          timestamp,
          volume,
        ]);
      });
    });
    return candlesData;
  }

  getExchanges() {
    return this.$http({
      method: 'GET',
      url: `http://${this.servicesRegistry.trader}/get_exchanges`,
      cache: true,
    });
  }

  loadExchange(name) {
    return name;
  }

  getMarket(name = null) {
    return this.$http({
      method: 'GET',
      url: `http://${this.servicesRegistry.trader}/get_market`,
      cache: true,
      params: {
        name,
      },
    });
  }
}
