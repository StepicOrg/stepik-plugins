App.AdminQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      image_id: 1
      memory: 64
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
