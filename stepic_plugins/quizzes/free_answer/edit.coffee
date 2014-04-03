App.FreeAnswerQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      manual_scoring: false

    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
