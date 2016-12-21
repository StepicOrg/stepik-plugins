export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      options: [{
          answer: '0',
          max_error: '0'
        }]
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Actions
  //
  actions: {
    addOption: function () {
      return this.get('source.options').pushObject({
        answer: '0',
        max_error: '0'
      });
    },
    removeOption: function () {
      return this.get('source.options').popObject();
    }
  }
});
