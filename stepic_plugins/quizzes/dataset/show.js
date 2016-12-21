import 'stepic/app';
import AutoResizeTextView from 'stepic/views/auto-resize-text';

export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  dataset_not_downloaded: true,
  //
  // Simple computed properties
  //
  is_textarea_disabled: Em.computed.or('disabled', 'dataset_not_downloaded'),
  AutoResizeTextView: AutoResizeTextView,
  //
  // Computed property functions
  //
  placeholder: function () {
    if (this.get('disabled')) {
      if (this.get('reply_url')) {
        return 'You can download your submission';
      }
      return '';
    } else {
      if (this.get('dataset_not_downloaded')) {
        return 'Download dataset first';
      } else {
        return 'Type your answer here...';
      }
    }
  }.property('disabled', 'reply_url', 'dataset_not_downloaded'),
  //
  // Event handlers
  //
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {file: ''});
      this.sendAction('replyUpdated', this.get('reply'));
      this.sendAction('isReplyReadyUpdated', false);
    }
  }.on('init'),
  //
  // Methods
  //
  didInsertElement: function () {
    var markLoaded;
    markLoaded = () => {
      this.send('download_started');
      return this.$().siblings('.get_dataset').addClass('secondary');
    };
    this.$().siblings('.get_dataset').click(() => {
      return markLoaded();
    });
    this.$().siblings('.get_dataset').on('contextmenu', () => {
      return setTimeout(markLoaded, 1000);
    });
    return this._super.apply(this, arguments);
  },
  //
  // Actions
  //
  actions: {
    download_started: function () {
      this.set('dataset_not_downloaded', false);
      this.sendAction('isReplyReadyUpdated', true);
    }
  }
});
