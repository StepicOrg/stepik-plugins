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
    didInsertElement: function() {
      var _this = this;
      $('.get_dataset').click(function() {
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
