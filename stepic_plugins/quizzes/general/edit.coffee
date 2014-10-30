App.GeneralQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      code: """
          #This is sample general quiz

          def solve():
              return '42'

          def check(reply):
              return int(reply) == 42

      """
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
