App.StringQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply')?
      @set 'reply',
        text: ''
  ).on('init')