export default Em.Component.extend({
  is_empty_text: Em.computed.equal('reply.text', ''),
  attachments: Em.computed.alias('reply.attachments'),
  is_embedded: Em.computed.oneWay('global_state.is_embedded'),
  has_only_files: Em.computed.and('is_empty_text', 'attachments.length', 'disabled'),
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {
        text: '',
        attachments: []
      });
      this.sendAction('replyUpdated', this.get('reply'));
    }
  }.on('init')
});
