import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  images: [
    {
      id: 3,
      name: 'Ubuntu 14.04'
    },
    {
      id: 4,
      name: 'Ubuntu 14.04 (imagemagick, ffmpeg)'
    },
    {
      id: 5,
      name: 'Ubuntu 14.04 (dbms)'
    },
    {
      id: 6,
      name: 'Ubuntu 14.04 (web)'
    },
    {
      id: 2,
      name: 'Ubuntu 14.04 (deprecated)'
    }
  ],
  CodeEditorView: CodeEditorView,
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      image_id: 3,
      memory: 64,
      is_bootstrap: false,
      bootstrap_script: '# This script provides the ability to configure a virtual machine in order\n# to prepare it for this challenge. It runs for every virtual machine created\n# prior to assigning it to a user. The execution time is limited to 5 minutes.',
      test_scenario: '# This is a sample Linux challenge test scenario\n\ndef test_connection(s):\n    assert s.run(\'true\').succeeded, "Could not connect to server"\n\n\ndef test_django_installed(s):\n    assert s.run(\'python -c "import django"\').succeeded, "Django is not installed"\n\n\ndef test_file_content(s):\n    file_content = s.run(\'cat /home/box/key.txt\')\n    assert \'secret\' in file_content, "Incorrect file content"'
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
