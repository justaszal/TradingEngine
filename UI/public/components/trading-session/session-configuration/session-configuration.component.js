import template from './session-configuration.html';
// import angular from 'angular';

const sessionConfigurationComponent = {
  bindings: {
    marketData: '<',
    onSessionStart: '&',
  },
  template,
  controller: class sessionConfiguration {
    constructor($scope, $timeout) {
      this.$timeout = $timeout;
    }
    $onInit() {
      this.currencies = [];
      this.selectedCurrency = '';
      this.selectedSymbol = '';
      this.selectedExchange = '';

      this.symbols = [];
      this.tickersList = [];
      this.exchanges_data = {};
      this.exchange_data = {};

      this.tickersListLimit = 5;
    }

    $onChanges(changes) {
      console.log(changes.marketData);
      if (
        changes &&
        changes.marketData.currentValue &&
        changes.marketData.currentValue.exchanges_data
      ) {
        [this.selectedExchange] = this.marketData.exchanges;
        this.exchanges_data = this.marketData.exchanges_data;
        this.initDropdowns();
        this.updateMaterializeSelect();
      }
    }

    updateMaterializeSelect() {
      /* eslint-disable no-undef */
      this.$timeout(() => {
        $('select').material_select();
      });
      /* eslint-disable no-undef */
    }

    initDropdowns() {
      this.exchange_data = this.marketData.exchanges_data[this.selectedExchange];
      this.symbols = this.exchange_data.symbols;
      [this.selectedSymbol] = this.symbols;
      [this.selectedCurrency] = this.exchange_data.currencies.base_currencies;
      [this.selectedSymbol] = this.exchange_data.currencies.currencies[this.selectedCurrency];
    }

    onExchangeSelect() {
      this.initDropdowns();
      this.tickersList = [];
      this.updateMaterializeSelect();
    }

    onCurrencySelect() {
      this.tickersList = [];
      [this.selectedSymbol] = this.exchange_data.currencies.currencies[this.selectedCurrency];
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
  },
};

export default sessionConfigurationComponent;
