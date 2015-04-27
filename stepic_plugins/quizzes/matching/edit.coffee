App.MatchingQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      preserve_firsts_order: true
      pairs: [{first: 'Sky', second: 'Blue'}, {first: 'Sun', second: 'Orange'}, {first: 'Grass', second: 'Green'}]
    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @get('source')

  setBindings: (->
    dragSource = null
    component = @
    options = @$('.matching-pair')
    options.off()
    .on 'dragstart', (e)->
      dragSource = @
      e.originalEvent.dataTransfer.setData 'text/html', @outerHTML
    .on 'dragover', (e)->
      e.preventDefault()
    .on 'drop', (e)->
      if options.index(dragSource) > options.index(@)
        $(@).before dragSource
      else
        $(@).after dragSource
      new_options = []
      component.$('.matching-pair').each (i,v)->
        new_options.push
          first: $(v).find('.first').val()
          second: $(v).find('.second').val()
      component.set 'source.pairs', new_options
      Em.run.next -> component.setBindings()
  ).on('didInsertElement')

  actions:
    addPair: ->
      @get('source.pairs').pushObject(
        first: ''
        second: ''
      )
      Em.run.next => @setBindings()

    removePair: (pair)->
      @set 'source.pairs', @get('source.pairs').without(pair)
      Em.run.next => @setBindings()

