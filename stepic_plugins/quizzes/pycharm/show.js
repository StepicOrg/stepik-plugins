import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  CodeEditorView: CodeEditorView,

  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {
        score: '0',
        solution: [{
            name: 'hello_world.py',
            text: 'print("Hello, world! My name is Liana")'
          }]
      });
      return this.sendAction('replyUpdated', this.get('reply'));
    }
  }.on('init')
});
