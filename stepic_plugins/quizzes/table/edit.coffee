App.TableQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    name_columns = ['First column', 'Second column', 'Third column']

    default_source =
        rows: [
             {name: 'First row', columns: ({name: column, answer: false} for column in name_columns)},
             {name: 'Second row', columns: ({name: column, answer: false} for column in name_columns)},
             {name: 'Third row', columns: ({name: column, answer: false} for column in name_columns)}
          ]
        is_checkbox: true
        name_columns: ['First column', 'Second column', 'Third column']
        name_rows: 'Rows: '
    @set 'source',
      @get('source') || default_source

  picker_view: Em.computed 'source.is_checkbox', ->
    if @get('source.is_checkbox')
      Em.Checkbox
    else
      Em.RadioButton
      
     
  get_source: ->
    @get('source')
    
 
  actions:
    log: ->
      console.log(@get('source'))
    
    add_row: ->
      new_rows = @get('source.rows').slice()
      new_rows.push({name: 'Next row', columns: ({name: column, answer: false} for column in @get('source.name_columns'))})
      @set 'source.rows', new_rows 

    delete_row: ->
      if (@get('source.rows').length > 1)
        new_rows = @get('source.rows').slice()
        new_rows.pop()
        @set 'source.rows', new_rows