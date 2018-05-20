import template from './navigation.component.html';
import style from './navigation.scss';

const NavigationComponent = {
  template,
  controller: class NavigationComponent {
    constructor($state) {
      this.$state = $state;
    }

    route(path) {
      this.$state.go(path);
    }
  },
};

export default NavigationComponent;
