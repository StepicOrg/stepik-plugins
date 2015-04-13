App.FreeAnswerQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply')?
      @set 'reply',
        text: ''
        attachments: []
  ).on('init')
