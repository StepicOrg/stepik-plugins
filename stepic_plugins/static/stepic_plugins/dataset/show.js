(function() {
  App.DatasetQuizComponent = Em.Component.extend({
    is_dataset_downloaded: false,
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          text: ''
        });
      }
    },
    is_input_disabled: (function() {
      return this.get('disabled') || !this.get('is_dataset_downloaded');
    }).property('disabled', 'is_dataset_downloaded'),
    didInsertElement: function() {
      var _this = this;
      this.$('.get_dataset').click(function() {
        return _this.get('controller').send('download_started');
      });
      return this._super.apply(this, arguments);
    },
    actions: {
      download_started: function() {
        return this.set('is_dataset_downloaded', true);
      }
    }
  });

}).call(this);
