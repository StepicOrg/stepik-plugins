(function() {
  App.GeogebraQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        ggbbase64: ''
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      return this.get('source');
    }
  });

}).call(this);
