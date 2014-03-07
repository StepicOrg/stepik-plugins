App.ChoiceQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')
      initial_choices = @get('dataset.options').map -> false
      @set 'reply',
        choices: initial_choices

    selections = _(@get('dataset.options')).zip(@get('reply.choices'))
    .map ([text, is_checked]) ->
        text: text
        is_checked: is_checked

    @set 'selections',
      selections

  picker_view: (->
    if @get('dataset.is_multiple_choice')
      Em.Checkbox
    else
      Em.RadioButton
  ).property('dataset.is_multiple_choice')

  onSelectionChanged: (->
    @set 'reply',
      choices: @get('selections').mapBy('is_checked')
  ).observes('selections.@each.is_checked')
