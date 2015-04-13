App.NumberQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply')?
      @set 'reply',
        number: '0' # use string for number to cope with big decimals
  ).on('init')
