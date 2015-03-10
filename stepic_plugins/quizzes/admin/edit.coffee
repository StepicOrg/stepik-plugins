App.AdminQuizEditorComponent = Em.Component.extend
  init: ->
    @_super()
    default_source =
      images: [
        # For now only hardcoded options
        {id: 3, name: "Ubuntu 14.04"},
        {id: 2, name: "Ubuntu 14.04 (deprecated)"}
      ]
      memory: 64
      is_bootstrap: false
      bootstrap_script: """
        # This script provides the ability to configure a virtual machine in order
        # to prepare it for this quiz. It runs for every virtual machine created.
    """
      test_scenario: """
        # This is sample admin quiz

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
