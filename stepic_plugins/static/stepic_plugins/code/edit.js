(function() {
  App.CodeQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        code: "#This is sample code quiz\nimport random\n\ndef generate():\n    num_tests = 10\n    tests = []\n    for test in range(num_tests):\n        a = random.randrange(10)\n        b = random.randrange(10)\n        test_case = \"{} {}\".format(a, b)\n        tests.append(test_case)\n    return tests\n\n\ndef solve(dataset):\n    a, b = dataset.split()\n    return str(int(a)+int(b))\n\n\ndef check(reply, clue):\n    return int(reply) == int(clue)",
        execution_time_limit: "5",
        execution_memory_limit: "256",
        templates_data: ""
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      this.set('source.execution_time_limit', this.get('source.execution_time_limit').toString());
      this.set('source.execution_memory_limit', this.get('source.execution_memory_limit').toString());
      return this.get('source');
    },
  });

}).call(this);
