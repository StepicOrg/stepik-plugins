var n;
export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      table_size: 3,
      is_grid: true,
      is_gorbov_table: false,
      is_font_randomized: false,
      is_color_randomized: false
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Observer function
  //
  isFontRandomizedSelected: function () {
    if (this.get('source.is_grid')) {
      return this.set('source.is_font_randomized', false);
    }
  }.observes('source.is_grid'),
  //
  // Actions
  //
  actions: {
    clickCell: function (cell) {
      return true;
    }
  },
  //
  // Other
  //
  table_size_options: function () {
    var i, results;
    results = [];
    for (n = i = 3; i <= 10; n = ++i) {
      results.push({
        value: n,
        label: n + 'x' + n
      });
    }
    return results;
  }()
});
