App.AdminQuizComponent = Em.Component.extend
  init: ->
    @_super()
    @set 'reply', {}
    self = @

    $.getScript '/static/stepic_plugins/admin/term.js', ->
      $.getScript '/static/stepic_plugins/admin/tty.js', ->
        tty.on 'open window', (window) ->
          self.set 'terminalWindow', window
          self.set 'isTerminalLoading', false

        tty.on 'close window', ->
          self.set 'terminalWindow', null

        tty.on 'disconnect', ->
          # in case of unsuccessful sockjs connection while opening terminal
          # make it possible to try to open terminal again
          self.set 'isTerminalLoading', false

    $.getScript '/static/stepic_plugins/admin/sockjs.min.js'
    $.getScript '/static/stepic_plugins/admin/base64.min.js'

  actions:
    toggleTerminal: ->
      if not @get 'isTerminalOpened'
        @set 'isTerminalLoading', true
        @send 'openTerminal'
      else
        @send 'closeTerminal'

    openTerminal: ->
      if @get 'isTerminalOpened'
        return
      console.log "Connecting to kaylee '#{@get 'dataset.kaylee_url'}'
        terminal id: #{@get 'dataset.terminal_id'}"
      tty.open @get('dataset.kaylee_url'), @get('dataset.terminal_id')

    closeTerminal: ->
      @get('terminalWindow').destroy() if @get 'terminalWindow'

  isTerminalOpened: (->
    !!@get 'terminalWindow'
  ).property 'terminalWindow'

  isTerminalControlsDisabled: Em.computed.or 'disabled', 'isTerminalLoading'

  destroyComponent: (->
    @send 'closeTerminal'
  ).on('willDestroyElement')
