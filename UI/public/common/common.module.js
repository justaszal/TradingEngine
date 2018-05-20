import angular from 'angular';
import HeaderTraderComponent from './header-trader/header-trader.component';
import AppComponent from './app.component';
import NavigationComponent from './navigation/navigation.component';

export default angular
  .module('app.common', [])
  .config(($stateProvider) => {
    $stateProvider
      .state('home', {
        abstract: true,
        url: '/',
        component: 'app',
      })
      .state('home.backtest', {
        url: 'backtest',
        component: 'backtest',
      })
      .state('home.live-trade', {
        url: 'live-trade',
        component: 'liveTrade',
      });
  })
  .component('app', AppComponent)
  .component('headerTrader', HeaderTraderComponent)
  .component('navigation', NavigationComponent)
  .name;
