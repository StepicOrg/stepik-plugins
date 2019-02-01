App.UnityQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      file: 'empty_file'

    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')


App.UploadFile = Ember.TextField.extend(
  tagName: "input"
  attributeBindings: ["name"]
  type: "file"
  file: null
  change: (e) ->
    reader = new FileReader()
    that = this
    reader.onload = (e) ->
      fileToUpload = e.target.result
      Ember.run ->
        that.set "file", fileToUpload
        return

      return

    reader.readAsDataURL e.target.files[0]
)
