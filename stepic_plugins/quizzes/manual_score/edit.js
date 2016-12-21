export default Em.Component.extend({
  setInitial: function () {
    const default_source = {};
    this.set('source', this.get('source') || default_source);
    this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
