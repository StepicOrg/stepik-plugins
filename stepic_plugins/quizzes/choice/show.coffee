App.ChoiceQuizComponent = Em.Component.extend
  setInitial: (->
    if not @get('reply.choices')
      initial_choices = @get('dataset.options').map -> false
      @set 'reply',
        choices: initial_choices
    @onSelectionChanged()
  ).on('init')

  selections: Em.computed 'dataset', 'reply', ->
    _(@get('dataset.options')).zip(@get('reply.choices')).map([text, is_checked]) ->
      text: text
      is_checked: is_checked

  picker_view: Em.computed 'dataset.is_multiple_choice', ->
    if @get('dataset.is_multiple_choice')
      Em.Checkbox
    else
      Em.RadioButton

  onSelectionChanged: (->
    choices = @get('selections').mapBy('is_checked')
    @set 'reply',  choices: choices
    @set 'is_reply_ready',
      @get('dataset.is_multiple_choice') or _.some(choices)
  ).observes('selections.@each.is_checked')
