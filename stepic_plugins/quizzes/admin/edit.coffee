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
        # to prepare it for this challenge. It runs for every virtual machine created
        # prior to assigning it to a user. The execution time is limited to 5 minutes.
    """
      test_scenario: """
        # This is a sample Linux challenge test scenario

        def test_connection(s):
            assert s.run('true').succeeded, "Could not connect to server"


        def test_django_installed(s):
            assert s.run('python -c "import django"').succeeded, "Django is not installed"


        def test_file_content(s):
            file_content = s.run('cat /home/box/key.txt')
            assert 'secret' in file_content, "Incorrect file content"
      """
    @set 'source',
      @get('source') || default_source

  get_source: ->
    @get('source')
