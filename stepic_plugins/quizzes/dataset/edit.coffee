App.DatasetQuizEditorComponent = Em.Component.extend
  setInitial: (->()
    default_source =
      code: """
          #This is sample dataset quiz
          import random

          def generate():
              a = random.randrange(10)
              b = random.randrange(10)
              return "{} {}".format(a, b)


          def solve(dataset):
              a, b = dataset.split()
              return str(int(a)+int(b))


          def check(reply, clue):
              return int(reply) == int(clue)

          tests = [
              ("2 2", "4", "4"),
              ("1 5", "6", "6")
          ]
      """
    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @get('source')
