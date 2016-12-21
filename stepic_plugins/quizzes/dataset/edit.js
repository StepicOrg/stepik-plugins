import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  //
  // undefined
  //
  CodeEditorView: CodeEditorView,
  setInitial: function () {
    var default_source;
    default_source = {code: '#This is sample dataset challenge\nimport random\n\ndef generate():\n    a = random.randrange(10)\n    b = random.randrange(10)\n    return "{} {}\\n".format(a, b)\n\n\ndef solve(dataset):\n    a, b = dataset.split()\n    return str(int(a)+int(b))\n\n\ndef check(reply, clue):\n    return int(reply) == int(clue)\n\ntests = [\n    ("2 2\\n", "4", "4"),\n    ("1 5\\n", "6", "6")\n]'};
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
