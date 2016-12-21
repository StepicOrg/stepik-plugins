export default Em.Component.extend({
  //
  // Simple computed properties
  //
  isTerminalControlsDisabled: Em.computed.or('disabled', 'isTerminalLoading'),
  //
  // Computed property functions
  //
  isTerminalOpened: function () {
    return !!this.get('terminalWindow');
  }.property('terminalWindow'),
  //
  // Event handlers
  //
  destroyComponent: function () {
    return this.send('closeTerminal');
  }.on('willDestroyElement'),
  setInitial: function () {
    var self;
    this.set('reply', {});
    this.sendAction('replyUpdated', this.get('reply'));
    this.set('isTerminalLoading', true);
    self = this;
    $.getScript('/static/frontend/plugins/admin/term.js', function () {
      return $.getScript('/static/frontend/plugins/admin/tty.js', function () {
        tty.on('open window', function (termWindow) {
          var leftOffset, topOffset;
          self.set('terminalWindow', termWindow);
          self.set('isTerminalLoading', false);
          topOffset = Math.max(0, $(window).height() - $(termWindow.element).outerHeight()) / 2;
          leftOffset = Math.max(0, $(window).width() - $(termWindow.element).outerWidth()) / 2;
          $(termWindow.element).css('top', topOffset + $(window).scrollTop());
          return $(termWindow.element).css('left', leftOffset + $(window).scrollLeft());
        });
        tty.on('close window', function () {
          return self.set('terminalWindow', null);
        });
        tty.on('disconnect', function () {
          return self.set('isTerminalLoading', false);
        });
        return self.set('isTerminalLoading', false);
      });
    });
    return $.getScript('/static/frontend/plugins/admin/base64.min.js');
  }.on('init'),
  //
  // Actions
  //
  actions: {
    toggleTerminal: function () {
      if (!this.get('isTerminalOpened')) {
        this.set('isTerminalLoading', true);
        return this.send('openTerminal');
      } else {
        return this.send('closeTerminal');
      }
    },
    openTerminal: function () {
      if (this.get('isTerminalOpened')) {
        return;
      }
      console.log('Connecting to kaylee \'' + this.get('dataset.kaylee_url') + '\' terminal id: ' + this.get('dataset.terminal_id'));
      return tty.open(this.get('dataset.kaylee_url'), this.get('dataset.terminal_id'));
    },
    closeTerminal: function () {
      if (this.get('terminalWindow')) {
        return this.get('terminalWindow').destroy();
      }
    }
  }
});
