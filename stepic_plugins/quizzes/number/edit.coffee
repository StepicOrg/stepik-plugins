App.NumberQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      asnwer: '0'
      max_error: '0'
    @set 'source',
      @get('source') || default_source


  get_source: ->
    @get('source')
