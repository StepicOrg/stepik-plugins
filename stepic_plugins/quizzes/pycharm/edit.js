export default Em.Component.extend({
  //
  // undefined
  //
  setInitial: function () {
    var default_source;
    default_source = {
      title: 'PyCharm Problem',
      files: [{
          name: 'hello_world.py',
          text: 'print("Hello, world! My name is type your name")',
          placeholders: [{
              line: 0,
              start: 32,
              length: 14,
              hint: 'Type your name here',
              possible_answer: 'Liana'
            }]
        }],
      test: [{
          name: 'tests.py',
          text: 'from test_helper import run_common_tests, failed, passed, get_answer_placeholders\n\ndef test_is_alpha():\n    window = get_answer_placeholders()[0]\n    splitted = window.split()\n    for s in splitted:\n        if not s.isalpha():\n            failed("Please use only English characters this time.")\n            return\n    passed()\n\nif __name__ == \'__main__\':\n    run_common_tests("You should enter your name")\n    test_is_alpha()'
        }]
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init')
});
