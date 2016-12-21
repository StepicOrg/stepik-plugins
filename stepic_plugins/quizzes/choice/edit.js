export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      is_multiple_choice: false,
      is_always_correct: false,
      sample_size: 3,
      preserve_order: false,
      is_html_enabled: true,
      is_options_feedback: false,
      options: [
        {
          is_correct: false,
          text: 'Choice A',
          feedback: ''
        },
        {
          is_correct: true,
          text: 'Choice B',
          feedback: ''
        },
        {
          is_correct: false,
          text: 'Choice C',
          feedback: ''
        }
      ]
    };
    this.set('source', this.get('source') || default_source);
    this.set('is_feedback_mode', false);
    this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Actions
  //
  actions: {
    addOption: function () {
      this.get('source.options').pushObject({
        is_correct: false,
        text: '',
        feedback: ''
      });
      return this.set('source.sample_size', parseInt(this.get('source.sample_size'), 10) + 1);
    },
    removeOption: function (option) {
      this.set('source.options', this.get('source.options').without(option));
      if (this.get('source.options.length') < this.get('source.sample_size') && this.get('source.sample_size') > 1) {
        return this.set('source.sample_size', this.get('source.options.length'));
      }
    },
    toggleFeedbackMode: function () {
      this.toggleProperty('is_feedback_mode');
    }
  }
});
