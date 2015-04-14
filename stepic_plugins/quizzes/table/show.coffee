App.TableQuizComponent = Em.Component.extend
  setInitial: (->
    default_reply =
        choices: ({name_row: row, columns: ({name: column, answer: false} for column in @get('dataset.columns'))} for row in @get('dataset.rows'))
            
    @set 'reply',
      @get('reply') || default_reply
  ).on('init')
    

  picker_view: Em.computed 'dataset.is_checkbox', ->
    if @get('dataset.is_checkbox')
      Em.Checkbox
    else
      Em.RadioButton