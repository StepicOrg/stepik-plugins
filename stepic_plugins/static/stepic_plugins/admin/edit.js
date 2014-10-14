(function() {
  App.AdminQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        image_id: 2,
        memory: 64,
        test_scenario: "#This is sample admin quiz\nfrom zoe.fixtures import s\n\n\ndef test_connection(s):\n    assert s.run('true').succeeded, \"Could not connect to server\"\n\n\ndef test_django_installed(s):\n    assert s.run('python -c \"import django\"').succeeded, \"Django is not installed\"\n\n\ndef test_file_content(s):\n    assert 'secret' in s.run('cat /root/key.txt'), \"Incorrect file content\""
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      return this.get('source');
    }
  });

}).call(this);