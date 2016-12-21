export default Em.Component.extend({
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {answer: ''});
      this.sendAction('replyUpdated', this.get('reply'));
    }
  }.on('init')
});
