App.MatchingQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply.ordering')
      N = @get('dataset.pairs.length')
      initial_ordering = Array.apply(null, {length: N}).map(Number.call, Number) #  0, 1, 2, 3, ...
      @set 'reply',
        ordering: initial_ordering
    @set 'options', ({index: index, second: @get('dataset.pairs')[index].second} for index in @get('reply.ordering'))
  ).on('init')

  onOptionsChanged: (->
    @set 'reply',  ordering: (option.index for option in @get('options'))
  ).observes('options')

  actions:
    moveIt: (row, shift)->
      options = @get('options').slice()
      pos = options.indexOf(row)
      options[pos] = options[pos + shift]
      options[pos + shift] = row
      @set 'options', options
