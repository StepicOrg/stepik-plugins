App.CodeQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        code: ''
        language: null
      unless @get('is_multiple_langs')
       @set 'user_lang', @get('langs.firstObject')
       @setInitialCode()

  user_lang: Em.computed.alias 'reply.language'
  user_code: Em.computed.alias 'reply.code'
  is_multiple_langs: Em.computed.gt 'langs.length', 1
  file_value: null

  setLangVisually: (->
    if @get('user_lang') and @get('is_multiple_langs') 
      @$(".lang-selector").val( @get('user_lang') )
  ).on('didInsertElement')

  langs: (->
    _.keys @get('content.options.code_templates')
  ).property('content')

  code_template: (->
    if @get('user_lang')
      @get('content.options.code_templates')[@get('user_lang')]
  ).property('user_lang')

  initial_code: (->    
    if @get('previous_reply.language') == @get('user_lang')
      @get('previous_reply.code')
    else
      @get('code_template')
  ).property('user_lang')

  uploadFile: (->
    file = @$('input[type="file"]')[0].files[0]
    return unless file
    reader = new FileReader()
    reader.onload = =>
      @set 'reply.code', reader.result
    reader.readAsText file.slice()
  ).observes('file_value')

  setInitialCode: ((forced=false)->
    if not @get('user_code') and @get('user_lang')
      @set 'user_code', @get('initial_code')
  ).observes('user_lang')

  onLangSelected: (->
    @set 'is_reply_ready', !!@get('user_lang')
  ).observes('user_lang').on('init')

  actions:
    setLang: ->
      lang = @$('.lang-selector').val()
      if ( @get('initial_code') is @get('user_code') ) or \
        not @get('user_code') or \
        confirm('This will erase your changes!')
          @set 'user_lang', lang
          @set 'user_code', @get('initial_code')