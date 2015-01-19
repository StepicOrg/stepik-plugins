(function() {
  App.PycharmQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          score: 0
        });
      }
    }
  });

}).call(this);
