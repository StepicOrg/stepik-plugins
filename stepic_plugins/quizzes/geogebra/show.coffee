App.GeogebraQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        answer: true
