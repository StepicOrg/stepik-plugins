App.ChoiceQuizEditorComponent = Em.Component.extend

  picker_view: (->
    if @get('is_multiple_choice')
      Em.Checkbox
    else
      Em.RadioButton
  ).property('is_multiple_choice')

  get_source: ->
    @set 'source.sample_size', parseInt(@get('source.sample_size'), 10)
    @get('source')

  actions:
    addOption: ->
      @get('source.options').pushObject(
        is_correct: false
        text: ''
      )

    removeOption: (option)->
      @set('source.options', @get('source.options').without(option))

