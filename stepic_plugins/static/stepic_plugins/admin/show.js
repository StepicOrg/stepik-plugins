(function() {
  App.AdminQuizComponent = Em.Component.extend({
    init: function() {
      var self;
      this._super();
      this.set('reply', {});
      this.set('isTerminalLoading', true);
      self = this;
      $.getScript('/static/stepic_plugins/admin/term.js', function() {
        return $.getScript('/static/stepic_plugins/admin/tty.js', function() {
          tty.on('open window', function(window) {
            self.set('terminalWindow', window);
            return self.set('isTerminalLoading', false);
          });
          tty.on('close window', function() {
            return self.set('terminalWindow', null);
          });
          tty.on('disconnect', function() {
            return self.set('isTerminalLoading', false);
          });
          return self.set('isTerminalLoading', false);
        });
      });
      $.getScript('/static/stepic_plugins/admin/sockjs.min.js');
      return $.getScript('/static/stepic_plugins/admin/base64.min.js');
    },
    actions: {
      toggleTerminal: function() {
        if (!this.get('isTerminalOpened')) {
          this.set('isTerminalLoading', true);
          return this.send('openTerminal');
        } else {
          return this.send('closeTerminal');
        }
      },
      openTerminal: function() {
        if (this.get('isTerminalOpened')) {
          return;
        }
        console.log("Connecting to kaylee '" + (this.get('dataset.kaylee_url')) + "' terminal id: " + (this.get('dataset.terminal_id')));
        return tty.open(this.get('dataset.kaylee_url'), this.get('dataset.terminal_id'));
      },
      closeTerminal: function() {
        if (this.get('terminalWindow')) {
          return this.get('terminalWindow').destroy();
        }
      }
    },
    isTerminalOpened: (function() {
      return !!this.get('terminalWindow');
    }).property('terminalWindow'),
    isTerminalControlsDisabled: Em.computed.or('disabled', 'isTerminalLoading'),
    destroyComponent: (function() {
      return this.send('closeTerminal');
    }).on('willDestroyElement')
  });

}).call(this);
