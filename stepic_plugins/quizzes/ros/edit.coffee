App.RosQuizEditorComponent = Em.Component.extend
  init: ->
      @_super()
      default_source =
        generatorlaunch: """
          <launch>
            <!-- TODO -->
          </launch>
        """
        solverlaunch: """
          <launch>
            <!-- TODO -->
          </launch>
        """
        generatorpy: """
          # This is sample ROS quiz generator
          import random
          import rospy, rospkg

          def generate():
            return '42'
        """
        solverpy: """
          # This is sample ROS quiz solver
          import rospy, rospkg

          def check():
            return True
        """
        paramsyaml: """
          # TODO
        """
      @set 'source',
        @get('source') || default_source

  get_source: ->
    @get('source')
