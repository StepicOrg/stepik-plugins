(function() {
  App.RosQuizComponent = Em.Component.extend({
    dataset_not_downloaded: true,
    placeholder: (function() {
      if (this.get('disabled')) {
        return 'You can download your submission';
      } else {
        if (this.get('dataset_not_downloaded')) {
          return 'Download dataset first';
        } else {
          return 'Type your answer here...';
        }
      }
    }).property('disabled', 'dataset_not_downloaded'),
    is_textarea_disabled: Em.computed.or('disabled', 'dataset_not_downloaded'),
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          resultset: ''
        });
      }
    },
    didInsertElement: function() {
      var markLoaded;
      markLoaded = (function(_this) {
        return function() {
          return _this.send('download_started');
        };
      })(this);
      this.$().siblings('.get_dataset').click((function(_this) {
        return function() {
          return markLoaded();
        };
      })(this));
      this.$().siblings('.get_dataset').on('contextmenu', (function(_this) {
        return function() {
          return setTimeout(markLoaded, 1000);
        };
      })(this));
      return this._super.apply(this, arguments);
    },
    actions: {
      download_started: function() {
        return this.set('dataset_not_downloaded', false);
      }
    }
  });

}).call(this);
