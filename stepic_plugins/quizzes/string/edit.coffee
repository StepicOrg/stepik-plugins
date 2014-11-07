App.StringQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      pattern: ""
      use_re: false
      match_substring: false
      case_sensitive: false
      code: ""
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
