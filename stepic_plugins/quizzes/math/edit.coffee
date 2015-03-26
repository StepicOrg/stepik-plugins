App.MathQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      answer: '2*x+y/z'
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
