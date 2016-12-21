export default Em.Component.extend({
  is_embedded: Em.computed.alias('global_state.is_embedded'),

  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {text: '', files: []});
      this.sendAction('replyUpdated', this.get('reply'));
    }
  }.on('init'),

  resetTextOnAttachment: function () {
    if (this.get('reply.files.length')) {
      this.set('reply.text', '');
    }
  }.observes('reply.files.@each')
});
