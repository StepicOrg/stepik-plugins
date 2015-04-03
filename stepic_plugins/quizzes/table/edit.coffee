App.TableQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
        rows: [
             {name: 'AAA', columns: [{name:'A', answer: false}, {name:'B', answer: false}, {name:'C', answer: false}]},
             {name: 'BBB', columns: [{name:'A', answer: false}, {name:'B', answer: false}, {name:'C', answer: false}]},
             {name: 'CCC', columns: [{name:'A', answer: false}, {name:'B', answer: false}, {name:'C', answer: false}]}
          ]
        is_multiple_choice: true
        name_columns: ['A', 'B', 'C']
    @set 'source',
      @get('source') || default_source

  picker_view: Em.computed 'source.is_multiple_choice', ->
    if @get('source.is_multiple_choice')
      Em.Checkbox
    else
      console.log("O_O")
      Em.RadioButton

  get_source: ->
    @get('source')
    
  