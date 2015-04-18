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

  didInsertElement: ->
    @setBindings()

  setBindings: ->
    dragSource = null
    component = @
    options = @$('.sorting-quiz__item')
    options.off()
    .on 'dragstart', (e)->
      dragSource = @
      $(@).addClass 'sorting-quiz__item-extracted'
      e.originalEvent.dataTransfer.setData 'text/html', @outerHTML
    .on 'dragover', (e)->
      options.removeClass('sorting-quiz__item-insert-before').removeClass 'sorting-quiz__item-insert-after'
      if options.index(dragSource) > options.index(@)
        $(@).addClass 'sorting-quiz__item-insert-before'
      else
        $(@).addClass 'sorting-quiz__item-insert-after'
      e.preventDefault()
    .on 'dragend', (e) ->
      options.removeClass('sorting-quiz__item-insert-before').removeClass('sorting-quiz__item-insert-after').removeClass 'sorting-quiz__item-extracted'
    .on 'dragleave', (e) ->
      options.removeClass('sorting-quiz__item-insert-before').removeClass 'sorting-quiz__item-insert-after'
    .on 'drop', (e)->
      if options.index(dragSource) > options.index(@)
        $(@).before dragSource
      else
        $(@).after dragSource
      new_options = []
      component.$('.sorting-quiz__item').each (i,v)->
        new_options.push
          index: $(v).find('.sorting-quiz__item_number').text()
          text: $(v).find('.sorting-quiz__item_text').text()
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
