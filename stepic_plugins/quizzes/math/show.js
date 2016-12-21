export default Em.Component.extend({
  //
  // undefined
  //
  is_embedded: Em.computed.oneWay('global_state.is_embedded'),
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {formula: ''});
      return this.sendAction('replyUpdated', this.get('reply'));
    }
  }.on('init')
});
