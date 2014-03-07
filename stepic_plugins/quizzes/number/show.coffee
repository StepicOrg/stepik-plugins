App.NumberQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        number: '0' # use string for number to cope with big decimals
