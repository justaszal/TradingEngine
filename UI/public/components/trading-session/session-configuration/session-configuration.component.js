import template from './session-configuration.html';
// import angular from 'angular';

const sessionConfigurationComponent = {
  bindings: {
    marketData: '<',
    onSessionStart: '&',
  },
  template,
  controller: class sessionConfiguration {
    constructor(sessionConfigurationService) {
      this.sessionService = sessionConfigurationService;
    }

    $onChanges(changes) {
      if (
        changes &&
        changes.marketData.currentValue &&
        changes.marketData.currentValue.exchanges_data
      ) {
        this.sessionService.initSession(this.marketData);
      }
    }

    onExchangeSelect() {
      this.sessionService.onExchangeSelect();
    }

    onCurrencySelect() {
      this.sessionService.onCurrencySelect();
    }

    addSelectedSymbol() {
      this.sessionService.addSymbol(
        this.sessionService.selectedCurrency,
        this.sessionService.selectedSymbol,
      );
    }

    removeSymbol(ticker) {
      this.sessionService.removeSymbol(ticker);
    }
  },
};

export default sessionConfigurationComponent;
