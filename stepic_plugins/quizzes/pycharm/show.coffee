App.PycharmQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        score: 0
        solution: [
          {
            name: 'hello_world.py'
            text: 'print("Hello, world! My name is Liana")'
          }
        ]
