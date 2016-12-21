export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      preserve_firsts_order: true,
      pairs: [
        {
          first: 'Sky',
          second: 'Blue'
        },
        {
          first: 'Sun',
          second: 'Orange'
        },
        {
          first: 'Grass',
          second: 'Green'
        }
      ]
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Actions
  //
  actions: {
    addPair: function () {
      return this.get('source.pairs').pushObject({
        first: '',
        second: ''
      });
    },
    removePair: function (pair) {
      return this.set('source.pairs', this.get('source.pairs').without(pair));
    }
  }
});
