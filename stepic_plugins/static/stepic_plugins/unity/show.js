(function() {
  App.UnityQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      console.log(this.get("quiz_file_url"));
      if (this.get('reply') == null) {
        return this.set('reply', {
          score: '0'
        });
      }
    }
  });

}).call(this);
