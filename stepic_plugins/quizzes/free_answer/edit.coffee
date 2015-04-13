App.FreeAnswerQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      manual_scoring: false

    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @get('source')
