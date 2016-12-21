export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source, option;
    default_source = {
      options: [
        'One',
        'Two',
        'Three'
      ]
    };
    this.set('source', this.get('source') || default_source);
    this.sendAction('sourceUpdated', this.get('source'));
    return this.set('options', function () {
      var i, len, ref, results;
      ref = this.get('source.options');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        option = ref[i];
        results.push({text: option});
      }
      return results;
    }.call(this));
  }.on('init'),
  //
  // Observer function
  //
  onOptionsChanged: function () {
    var option;
    return this.set('source.options', function () {
      var i, len, ref, results;
      ref = this.get('options');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        option = ref[i];
        results.push(option.text);
      }
      return results;
    }.call(this));
  }.observes('options', 'options.@each.text'),
  //
  // Actions
  //
  actions: {
    addOption: function () {
      return this.get('options').pushObject({text: ''});
    },
    removeOption: function (option) {
      return this.set('options', this.get('options').without(option));
    }
  }
});
