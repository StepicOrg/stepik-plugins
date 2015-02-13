App.MathQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      answer: ''
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
