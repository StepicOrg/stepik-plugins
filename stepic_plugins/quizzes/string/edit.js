import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  CodeEditorView: CodeEditorView,
  setInitial: function () {
    var default_source;
    default_source = {
      pattern: '',
      use_re: false,
      match_substring: false,
      case_sensitive: false,
      code: "# def check(reply):\n" +
            "#     \"\"\"Evaluate the learner's reply.\n" +
            "#\n" +
            "#     It should return 1 or True for the correct reply and 0 or False\n" +
            "#     for the incorrect one.\n" +
            "#\n" +
            "#     A partial solution may be scored using a float number from the\n" +
            "#     interval (0, 1). In such a case the learner total score for the\n" +
            "#     problem will be `step cost` * `score`.\n" +
            "#\n" +
            "#     :param reply: a string that is the learner's reply to the problem\n" +
            "#     :return: a score number (int or float) in range [0, 1]\n" +
            "#\n" +
            "#     \"\"\"\n" +
            "#     return reply == \"Hello\"\n" +
            "\n" +

            "# def solve():\n" +
            "#     \"\"\"Return a correct reply.\n" +
            "#\n" +
            "#     It is used to test the correctness of the `check` function.\n" +
            "#\n" +
            "#     :return: a string that is a correct reply to the problem\n" +
            "#\n" +
            "#     \"\"\"\n" +
            "#     return \"Hello\"\n"
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
