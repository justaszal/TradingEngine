import template from './search-bar.html';

export default {
  template,
  bindings: {
    searchText: '<',
    onUpdate: '&',
  },
  controller: class SearchBar {
    $onInit() {
      this.updateSearchText = SearchBar.updateSearchText;
    }

    static updateSearchText(searchText) {
      this.onUpdate({
        $event: {
          searchText,
        },
      });
    }
  },
};
