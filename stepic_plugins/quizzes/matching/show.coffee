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


  didInsertElement: ->
    @setBindings()

  setBindings: ->
    dragSource = null
    component = @
    options = @$('.matching-quiz__second-item')
    options.off()
    .on 'dragstart', (e)->
      dragSource = @
      $(@).addClass 'matching-quiz__second-item-extracted'
      e.originalEvent.dataTransfer.setData 'text/html', @outerHTML
    .on 'dragover', (e)->
      options.removeClass('matching-quiz__second-item-insert-before').removeClass 'matching-quiz__second-item-insert-after'
      if options.index(dragSource) > options.index(@)
        $(@).addClass 'matching-quiz__second-item-insert-before'
      else
        $(@).addClass 'matching-quiz__second-item-insert-after'
      e.preventDefault()
    .on 'dragend', (e) ->
      options.removeClass('matching-quiz__second-item-insert-before').removeClass('matching-quiz__second-item-insert-after').removeClass 'matching-quiz__second-item-extracted'
    .on 'dragleave', (e) ->
      options.removeClass('matching-quiz__second-item-insert-before').removeClass 'matching-quiz__second-item-insert-after'
    .on 'drop', (e)->
      if options.index(dragSource) > options.index(@)
        $(@).before dragSource
      else
        $(@).after dragSource
      new_options = []
      component.$('.matching-quiz__second-item').each (i,v)->
        new_options.push
          index: $(v).find('.matching-quiz__second-item_number').text()
          second: $(v).find('.matching-quiz__second-item_text').text()
      component.set 'options', new_options
      Em.run.next -> component.setBindings()

  actions:
    moveIt: (row, shift)->
      new_options = @get('options').slice()
      pos = new_options.indexOf(row)
      new_options[pos] = new_options[pos + shift]
      new_options[pos + shift] = row
      @set 'options', new_options
      Em.run.next => @setBindings()
