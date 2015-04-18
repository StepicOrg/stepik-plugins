App.ChoiceQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      is_multiple_choice: false
      is_always_correct: false
      sample_size: 3
      preserve_order: false
      options: [{is_correct: false, text: 'Choice A'}, {is_correct: true, text: 'Choice B'}, {is_correct: false, text: 'Choice C'}]
    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @set 'source.sample_size', parseInt(@get('source.sample_size'), 10)
    @get('source')

  didInsertElement: ->
    @setBindings()

  setBindings: ->
    dragSource = null
    component = @
    options = @$('.choice-option')
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
      component.$('.choice-option').each (i,v)->
        new_options.push {
            text: $(v).find('.text').val()
            is_correct: $(v).find('.is_correct').is(':checked')
        }
      component.set 'source.options', new_options
      Em.run.next -> component.setBindings()

  actions:
    addOption: ->
      @get('source.options').pushObject(
        is_correct: false
        text: ''
      )
      @set 'source.sample_size', (@get('source.sample_size') + 1)
      Em.run.next => @setBindings()

    removeOption: (option)->
      @set 'source.options', @get('source.options').without(option)
      if @get('source.options.length') < @get('source.sample_size') and @get('source.sample_size') > 1
        @set 'source.sample_size', @get('source.options.length')
      Em.run.next => @setBindings()
