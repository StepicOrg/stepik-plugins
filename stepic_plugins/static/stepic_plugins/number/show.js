(function() {
  App.NumberQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          number: '0'
        });
      }
    }
  });

}).call(this);
