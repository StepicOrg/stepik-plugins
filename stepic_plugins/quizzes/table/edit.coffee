App.TableQuizEditorComponent = Em.Component.extend
  setInitial: (->
    name_columns = ['First column', 'Second column', 'Third column']

    default_source =
        rows: [
            {name: 'First row', columns: (choice: false for column in name_columns)},
            {name: 'Second row', columns: (choice: false for column in name_columns)},
            {name: 'Third row', columns: (choice: false for column in name_columns)}
          ]
        options: {
            is_checkbox: false,
            is_randomize_rows: false,
            is_randomize_columns: false,
            sample_size: -1
          }
        columns: ['First column', 'Second column', 'Third column']
        description: 'Rows: '
    @set 'source',
      @get('source') || default_source
  ).on('init')

  getSource: ->
    @get('source')

  actions:
    addColumn: ->
      new_rows = @get('source.rows').slice()
      new_columns = @get('source.columns').slice()

      new_columns.push "New column"
      for row in new_rows
          row.columns.push choice: false
      @set 'source.rows', new_rows
      @set 'source.columns', new_columns

    deleteColumn: ->
      if (@get('source.columns').length > 1)
        new_rows = @get('source.rows').slice()
        new_columns = @get('source.columns').slice()
        new_columns.pop()

        for row in new_rows
          row.columns.pop()

        @set 'source.rows', new_rows
        @set 'source.columns', new_columns

    addRow: ->
      new_rows = @get('source.rows').slice()
      new_rows.push({name: 'Next row', columns: (choice: false for column in @get('source.columns'))})
      @set 'source.rows', new_rows

    deleteRow: ->
      if (@get('source.rows').length > 1)
        new_rows = @get('source.rows').slice()
        new_rows.pop()
        @set 'source.rows', new_rows