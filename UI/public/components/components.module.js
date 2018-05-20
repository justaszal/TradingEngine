import angular from 'angular';
import CryptoTableModule from './crypto-table/crypto-table.module';
import TradingSessionModule from './trading-session/trading-session.module';

export default angular
  .module('app.components', [
    CryptoTableModule,
    TradingSessionModule,
  ])
  .constant('servicesRegistry', {
    trader: '0.0.0.0:8081',
  })
  .name;
