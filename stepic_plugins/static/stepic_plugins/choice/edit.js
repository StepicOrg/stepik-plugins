(function() {
  App.ChoiceQuizEditorComponent = Em.Component.extend({
    init: function() {
      this._super();
      return console.log('iniit choiece quiz editor');
    },
    picker_view: (function() {
      if (this.get('is_multiple_choice')) {
        return Em.Checkbox;
      } else {
        return Em.RadioButton;
      }
    }).property('is_multiple_choice'),
    get_source: function() {
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
