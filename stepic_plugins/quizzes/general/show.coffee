App.GeneralQuizComponent = Em.Component.extend
  dataset_not_downloaded: true

  placeholder: (->
    if @get('disabled')
      'You can download your submission'
    else
      'Type your answer here...'
  ).property('disabled')

  is_textarea_disabled: Em.computed.or('disabled')

  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        file: ''
