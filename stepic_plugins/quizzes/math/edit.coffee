App.MathQuizEditorComponent = Em.Component.extend
  setInitial: (->
    default_source =
      answer: '2*x+y/z'
      numerical_test:
        z_re_min: '2'
        z_re_max: '3'
        z_im_min: '-1'
        z_im_max: '1'
        max_error: '1e-06'
        integer_only: false
    @set 'source',
      @get('source') || default_source
  ).on('init')

  get_source: ->
    @get('source')
