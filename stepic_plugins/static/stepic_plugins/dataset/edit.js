(function() {
  App.DatasetQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        code: "#This is sample dataset quiz\nimport random\n\ndef generate():\n    a = random.randrange(10)\n    b = random.randrange(10)\n    return \"{} {}\".format(a, b)\n\n\ndef solve(dataset):\n    a, b = dataset.split()\n    return str(int(a)+int(b))\n\n\ndef check(reply, clue):\n    return int(reply) == int(clue)\n\ntests = [\n    (\"2 2\", \"4\", \"4\"),\n    (\"1 5\", \"6\", \"6\")\n]"
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      return this.get('source');
    }
  });

}).call(this);
