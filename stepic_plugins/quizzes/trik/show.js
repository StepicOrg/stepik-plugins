export default Em.Component.extend({
  //
  // undefined
  //
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {studio_save: []});
      return this.sendAction('replyUpdated', this.get('reply'));
    }
  }.on('init')
});
