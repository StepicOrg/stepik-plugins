(function() {
  App.NumberQuizEditorComponent = Em.Component.extend({
    init: function() {
      this._super();
      return console.log(this.get('source'));
    },
    get_source: function() {
      return this.get('source');
    }
  });

}).call(this);
