App.CodeQuizEditorComponent = Em.Component.extend
  init: ->
      @_super()
      default_source =
        code: """
          #This is sample code quiz
          import random

          def generate():
              num_tests = 10
              tests = []
              for test in range(num_tests):
                  a = random.randrange(10)
                  b = random.randrange(10)
                  test_case = "{} {}".format(a, b)
                  tests.append(test_case)
              return tests


          def solve(dataset):
              a, b = dataset.split()
              return str(int(a)+int(b))


          def check(reply, clue):
              return int(reply) == int(clue)
        """
        execution_time_limit: '5'
        execution_memory_limit: '256'
        templates_data: ""
      @set 'source',
        @get('source') || default_source

  get_source: ->
    @set 'source.execution_time_limit', @get('source.execution_time_limit').toString()
    @set 'source.execution_memory_limit', @get('source.execution_memory_limit').toString()
    @get('source')
