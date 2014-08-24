App.ChoiceQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      is_multiple_choice: false
      is_always_correct: false
      sample_size: 3
      preserve_order: false
      options: [{is_correct: false, text: 'Choice 1'}, {is_correct: true, text: 'Choice 2'}, {is_correct: false, text: 'Choice 3'}]
    @set 'source',
      @get('source') || default_source



  picker_view: (->
    if @get('is_multiple_choice')
      Em.Checkbox
    else
      Em.RadioButton
  ).property('is_multiple_choice')

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
      Em.run.next => @setBindings()


    removeOption: (option)->
      @set('source.options', @get('source.options').without(option))
      Em.run.next => @setBindings()

