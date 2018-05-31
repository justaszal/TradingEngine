export default class sessionConfigurationService {
  constructor($timeout) {
    this.$timeout = $timeout;

    this.marketData = {};
    this.tickersList = [];
    this.symbols = [];

    this.selectedCurrency = '';
    this.selectedSymbol = '';
    this.selectedExchange = '';

    this.tickersListLimit = 5;
  }

  initSession(marketData) {
    this.marketData = marketData;
    this.setDefaultExchange();
    this.initDropdowns();
  }

  setDefaultExchange() {
    [this.selectedExchange] = this.marketData.exchanges;
    this.symbols = this.getCurrentExchange().symbols;
  }

  initDropdowns() {
    [this.selectedSymbol] = this.symbols;
    [this.selectedCurrency] = this.getCurrentExchange().currencies.base_currencies;
    [this.selectedSymbol] = this.getCurrentExchange().currencies.currencies[this.selectedCurrency];
    this.updateMaterializeSelect();
  }

  getCurrentExchange() {
    return this.selectedExchange ? this.marketData.exchanges_data[this.selectedExchange] : null;
  }

  getBaseCurrencies() {
    return (this.getCurrentExchange() &&
            this.getCurrentExchange().currencies.base_currencies)
           || {};
  }

  getSelectedSymbols() {
    return (this.getCurrentExchange() &&
            this.getCurrentExchange().currencies.currencies[this.selectedCurrency])
            || [];
  }

  updateMaterializeSelect() {
    /* eslint-disable no-undef */
    this.$timeout(() => {
      $('select').material_select();
    });
    /* eslint-disable no-undef */
  }

  onExchangeSelect() {
    this.initDropdowns();
    this.tickersList = [];
    this.updateMaterializeSelect();
  }


  onCurrencySelect() {
    this.tickersList = [];
    [this.selectedSymbol] = this.getCurrentExchange().currencies.currencies[this.selectedCurrency];
    this.updateMaterializeSelect();
  }

  addSymbol(currency, symbol) {
    const ticker = `${currency}/${symbol}`;

    if (this.tickersList.length < this.tickersListLimit &&
        this.tickersList.indexOf(ticker) === -1) {
      this.tickersList.push(ticker);
    }
  }

  removeSymbol(ticker) {
    const indexToRemove = this.tickersList.indexOf(ticker);

    if (indexToRemove !== -1) {
      this.tickersList.splice(indexToRemove, 1);
    }
  }
}
