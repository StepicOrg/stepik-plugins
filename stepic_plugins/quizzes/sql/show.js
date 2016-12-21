import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  CodeEditorView: CodeEditorView,
  setInitial: function () {
    this.set('reply', this.get('reply') || {solve_sql: ""});
    this.sendAction('replyUpdated', this.get('reply'));
  }.on('init')
});
