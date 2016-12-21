export default Em.Component.extend({
  setInitial: function () {
    var default_source = {
      task_id: '',
      is_makefile_required: false
    };
    this.set('source', this.get('source') || default_source);
    this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
