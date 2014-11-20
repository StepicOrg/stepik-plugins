App.CodeQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        code: ''
        language: null

  user_langBinding: 'reply.language'
  user_codeBinding: 'reply.code'

  langs: (->
    _.keys @get('content.options.code_templates')
  ).property('content')

  is_lang_selectable: (->
    not (@get('user_code') or @get('user_lang'))
  ).property('langs', 'user_lang')

  code_template: (->
    if @get('user_lang')
      @get('content.options.code_templates')[@get('user_lang')]
  ).property('user_lang')

  _set_initial_language: (->
    if @get('content') and @get('langs.length') == 1
      @set 'user_lang', @get('langs.firstObject')
  ).observes('langs').on('init')

  _set_initial_code: (->
    if not @get('user_code') and @get('user_lang')
      initial_code = if @get('previous_reply.language') == @get('user_lang')
      then @get('previous_reply.code')
      else @get('code_template')

      @set 'user_code', initial_code
  ).observes('user_lang')

  onLangSelected: (->
    @set 'is_reply_ready', not @get('is_lang_selectable')
  ).observes('is_lang_selectable').on('init')

  actions:
    setLang: (lang)->
      @set 'user_lang', lang
