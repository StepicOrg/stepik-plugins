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

  setInitial: (->()
    if not @get('reply')?
      @set 'reply',
        file: ''
  ).on('init')

  didInsertElement: ->
    markLoaded = => @send 'download_started'
    # sic! .get_dataset is outside of component
    @$().siblings('.get_dataset').click =>
      markLoaded()
    
    # "dowload as.." case
    @$().siblings('.get_dataset').on 'contextmenu', =>
      setTimeout markLoaded, 1000

    # @focus()
    @_super.apply(@, arguments)

  actions:
    download_started: ->
      @set 'dataset_not_downloaded', false
