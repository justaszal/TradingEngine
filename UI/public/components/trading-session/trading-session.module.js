import angular from 'angular';
import backtestComponent from './backtest/backtest.component';
import liveTradeComponent from './live-trade/live-trade.component';
import candlestickChartComponent from './candlestick-chart/candlestick-chart.component';
import candlestickChartService from './candlestick-chart/candlestick-chart.service';
import tradingSessionService from './trading-session.service';
import sessionConfigurationComponent
  from './session-configuration/session-configuration.component';
import symbolsFilter from './session-configuration/session-configuration.filter';

export default angular
  .module('tradingSessionModule', [])
  .component('backtest', backtestComponent)
  .component('liveTrade', liveTradeComponent)
  .component('candlestickChart', candlestickChartComponent)
  .component('sessionConfiguration', sessionConfigurationComponent)
  .factory('candlestickChartService', candlestickChartService)
  .service('tradingSessionService', tradingSessionService)
  .filter('symbolsFilter', symbolsFilter)
  .name;
