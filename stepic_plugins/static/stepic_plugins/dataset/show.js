(function() {
  App.DatasetQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          text: ''
        });
      }
    }
  });

}).call(this);
