App.PycharmQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply')?
      @set 'reply',
        score: 0
        solution: [
          {
            name: 'hello_world.py'
            text: 'print("Hello, world! My name is Liana")'
          }
        ]
  ).on('init')
