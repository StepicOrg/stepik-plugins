export default Em.Component.extend({
  setInitial: function () {
    var default_reply = {
      solution: [],
      makefile: []
    };
    this.set('reply', this.get('reply') || default_reply);
    this.sendAction('replyUpdated', this.get('reply'));
  }.on('init')
});
