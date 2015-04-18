App.SortingQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply.ordering')
      N = @get('dataset.options.length')
      initial_ordering = Array.apply(null, {length: N}).map(Number.call, Number) #  0, 1, 2, 3, ...
      @set 'reply',
        ordering: initial_ordering
    @set 'options', ({index: index, text: @get('dataset.options')[index]} for index in @get('reply.ordering'))
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
