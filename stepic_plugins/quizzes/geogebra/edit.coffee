App.GeogebraQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      ggbbase64: ''
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
