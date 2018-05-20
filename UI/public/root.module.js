import angular from 'angular';
import '@uirouter/angularjs';
import RootComponent from './root.component';
import ComponentsModule from './components/components.module';
import CommonModule from './common/common.module';
// import MocksModule from '../mocks/mocks';
import style from './root.scss';

export default angular.module('root', [
  'ui.router',
  ComponentsModule,
  CommonModule,
  // MocksModule,
])
  .config(($stateProvider, $urlRouterProvider) => {
    'ngInject';

    $urlRouterProvider.otherwise('/backtest');
  })
  .component('root', RootComponent)
  .name;
