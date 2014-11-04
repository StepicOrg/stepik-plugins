(function() {
  App.GeogebraQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          answer: true
        });
      }
    }
  });

}).call(this);
