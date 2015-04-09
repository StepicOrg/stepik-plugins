App.StringQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      pattern: ""
      use_re: false
      match_substring: false
      case_sensitive: false
      code: ""
    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @get('source')
