App.FreeAnswerQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        text: ''
        attachments: []
