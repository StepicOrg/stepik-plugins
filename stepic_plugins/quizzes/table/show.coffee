App.TableQuizComponent = Em.Component.extend
  init: ->
    @_super()
    if not @get('reply')?
      @set 'reply',
        choices: [[]]

  picker_view: Em.computed 'dataset.is_checkbox', ->
    if @get('dataset.is_checkbox')
      Em.Checkbox
    else
      Em.RadioButton

