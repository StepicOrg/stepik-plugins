export default Em.Component.extend({
  //
  // undefined
  //
  setInitial: function () {
    var default_source;
    default_source = {
      studio_save: [],
      fields_archive: []
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
