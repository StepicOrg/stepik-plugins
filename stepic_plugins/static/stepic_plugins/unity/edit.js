(function() {
  App.UnityQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        file: 'empty_file'
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      return this.get('source');
    }
  });

  App.UploadFile = Ember.TextField.extend({
    tagName: "input",
    attributeBindings: ["name"],
    type: "file",
    file: null,
    change: function(e) {
      var reader, that;
      reader = new FileReader();
      that = this;
      reader.onload = function(e) {
        var fileToUpload;
        fileToUpload = e.target.result;
        Ember.run(function() {
          that.set("file", fileToUpload);
        });
      };
      return reader.readAsDataURL(e.target.files[0]);
    }
  });

}).call(this);
