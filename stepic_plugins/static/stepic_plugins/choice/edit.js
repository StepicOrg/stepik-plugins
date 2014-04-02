(function() {
  App.ChoiceQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        is_multiple_choice: false,
        is_always_correct: false,
        sample_size: 3,
        preserve_order: false,
        options: []
      };
      return this.set('source', this.get('source') || default_source);
    },
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
