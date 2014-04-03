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
    _.keys @get('content.code_templates')
  ).property('content')

  is_lang_selectable: (->
    not (@get('user_code') or @get('user_lang'))
  ).property('langs', 'user_lang')

  code_template: (->
    if @get('user_lang')
      @get('content.code_templates')[@get('user_lang')]
  ).property('user_lang')

  _apply_template: (->
    if not @get('user_code') and @get('user_lang')
      @set 'user_code', @get('code_template')
  ).observes('user_lang')

  onLangSelected: (->
    @set 'is_reply_ready', not @get('is_lang_selectable')
  ).observes('is_lang_selectable').on('init')

  actions:
    setLang: (lang)->
      @set 'user_lang', lang
