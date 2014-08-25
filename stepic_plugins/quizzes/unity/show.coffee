App.UnityQuizComponent = Em.Component.extend
  init: ->
    @_super()
    console.log @get("quiz_file_url")
    if not @get('reply')?
      @set 'reply',
        score: '0'
