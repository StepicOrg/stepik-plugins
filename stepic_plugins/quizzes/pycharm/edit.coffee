App.PycharmQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      title: 'PyCharm Problem'
      files: [
        {
          name: 'hello_world.py'
          text: 'print("Hello, world! My name is type your name")'
          placeholders: [
            {
              line: 0
              start: 32
              length: 14
              hint: 'Type your name here'
              possible_answer: 'Liana'
            }
          ]
         }
      ]
      test: [
        {
          name: 'tests.py'
          text: """
          from test_helper import run_common_tests, failed, passed, get_answer_placeholders

          def test_is_alpha():
              window = get_answer_placeholders()[0]
              splitted = window.split()
              for s in splitted:
                  if not s.isalpha():
                      failed("Please use only English characters this time.")
                      return
              passed()

          if __name__ == '__main__':
              run_common_tests("You should enter your name")
              test_is_alpha()
        """
        }
      ]
    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @get('source')
