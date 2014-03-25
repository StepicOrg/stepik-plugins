(function() {
  App.ChoiceQuizEditorComponent = Em.Component.extend({
    picker_view: (function() {
      if (this.get('is_multiple_choice')) {
        return Em.Checkbox;
      } else {
        return Em.RadioButton;
      }
    }).property('is_multiple_choice'),
    get_source: function() {
      this.set('source.sample_size', parseInt(this.get('source.sample_size'), 10));
      return this.get('source');
    },
    actions: {
      addOption: function() {
        return this.get('source.options').pushObject({
          is_correct: false,
          text: ''
        });
      },
      removeOption: function(option) {
        return this.set('source.options', this.get('source.options').without(option));
      }
    }
  });

}).call(this);
