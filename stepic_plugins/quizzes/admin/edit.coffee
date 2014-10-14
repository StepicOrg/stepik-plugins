App.AdminQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      image_id: 2
      memory: 64
      test_scenario: """
        #This is sample admin quiz

        def test_connection(s):
            assert s.run('true').succeeded, "Could not connect to server"


        def test_django_installed(s):
            assert s.run('python -c "import django"').succeeded, "Django is not installed"


        def test_file_content(s):
            assert 'secret' in s.run('cat /root/key.txt'), "Incorrect file content"
      """
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
