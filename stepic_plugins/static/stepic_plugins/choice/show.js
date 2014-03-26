(function() {
  App.ChoiceQuizComponent = Em.Component.extend({
    init: function() {
      var initial_choices, selections;
      this._super();
      if (!this.get('reply.choices')) {
        initial_choices = this.get('dataset.options').map(function() {
          return false;
        });
        this.set('reply', {
          choices: initial_choices
        });
      }
      selections = _(this.get('dataset.options')).zip(this.get('reply.choices')).map(function(_arg) {
        var is_checked, text;
        text = _arg[0], is_checked = _arg[1];
        return {
          text: text,
          is_checked: is_checked
        };
      });
      return this.set('selections', selections);
    },
    picker_view: (function() {
      if (this.get('dataset.is_multiple_choice')) {
        return Em.Checkbox;
      } else {
        return Em.RadioButton;
      }
    }).property('dataset.is_multiple_choice'),
    onSelectionChanged: (function() {
      return this.set('reply', {
        choices: this.get('selections').mapBy('is_checked')
      });
    }).observes('selections.@each.is_checked')
  });

}).call(this);
