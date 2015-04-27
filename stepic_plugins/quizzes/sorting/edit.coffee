App.SortingQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      options: ['One', 'Two', 'Three']
    @set 'source',
      @get('source') || default_source
    # transform array of strings into array of objects -- otherwise binding in hbs won't work, see http://stackoverflow.com/a/13025595
    @set 'options', ({text: option} for option in @get('source.options'))
  ).on('init')

  onOptionsChanged: (->
    @set 'source.options', (option.text for option in @get('options'))
  ).observes('options', 'options.@each.text')

  get_source: ->
    @get('source')

  setBindings: (->
    dragSource = null
    component = @
    options = @$('.sort-option')
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
      component.$('.sort-option').each (i,v)->
        new_options.push $(v).find('.text').val()
      component.set 'source.options', new_options
      Em.run.next -> component.setBindings()
  ).on('didInsertElement')

  actions:
    addOption: ->
      @get('options').pushObject(
        text: ''
      )
      Em.run.next => @setBindings()

    removeOption: (option)->
      @set 'options', @get('options').without(option)
      Em.run.next => @setBindings()

