(function() {
  App.GeneralQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        code: "#This is sample general quiz\n\ndef solve():\n    return '42'\n\ndef check(reply):\n    return int(reply) == 42\n"
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      return this.get('source');
    }
  });

}).call(this);
