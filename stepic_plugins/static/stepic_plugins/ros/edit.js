(function() {
  App.RosQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        generatorlaunch: "<launch>\n  <!-- TODO -->\n</launch>",
        solverlaunch: "<launch>\n  <!-- TODO -->\n</launch>",
        generatorpy: "# This is sample ROS quiz generator\nimport random\nimport rospy, rospkg\n\ndef generate():\n  return '42'",
        solverpy: "# This is sample ROS quiz solver\nimport rospy, rospkg\n\ndef check():\n  return True",
        paramsyaml: "# TODO"
      };
      return this.set('source', this.get('source') || default_source);
    },
    get_source: function() {
      return this.get('source');
    }
  });

}).call(this);
