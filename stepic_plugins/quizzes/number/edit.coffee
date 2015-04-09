App.NumberQuizEditorComponent = Em.Component.extend
  setInitial: (->()
    default_source =
      answer: '0'
      max_error: '0'
    @set 'source',
      @get('source') || default_source
  ).on('init')


  get_source: ->
    @get('source')
