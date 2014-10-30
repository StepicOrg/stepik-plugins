(function() {
  App.GeneralQuizComponent = Em.Component.extend({
    dataset_not_downloaded: true,
    placeholder: (function() {
      if (this.get('disabled')) {
        return 'You can download your submission';
      } else {
        return 'Type your answer here...';
      }
    }).property('disabled'),
    is_textarea_disabled: Em.computed.or('disabled'),
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          file: ''
        });
      }
    }
  });

}).call(this);
