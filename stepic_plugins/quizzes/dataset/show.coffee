App.DatasetQuizComponent = Em.Component.extend
  dataset_not_downloaded: true

  placeholder: (->
    if @get('disabled')
      'You can download your submission'
    else
      if @get('dataset_not_downloaded')
        'Download dataset first'
      else
        'Type your answer here...'
  ).property('disabled', 'dataset_not_downloaded')

  is_textarea_disabled: Em.computed.or('disabled', 'dataset_not_downloaded')

  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        file: ''

  didInsertElement: ->
    # sic! .get_dataset is outside of component
    $('.get_dataset').click =>
      @get('controller').send 'download_started'
    # @focus()
    @_super.apply(@, arguments)

  actions:
    download_started: ->
      @set 'dataset_not_downloaded', false
