export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  checked: null,
  selections: [],
  //
  // Event handlers
  //
  setInitial: function () {
    var initial_choices;
    if (!this.get('reply.choices')) {
      initial_choices = this.get('dataset.options').map(function () {
        return false;
      });
      this.set('reply', {choices: initial_choices});
      this.sendAction('replyUpdated', this.get('reply'));
    } else {
      this.get('reply.choices').map((choosen, index) => {
        if (choosen) {
          return this.set('checked', index);
        }
      });
    }
    this.set('is_reply_ready', this.get('dataset.is_multiple_choice') || _.some(this.get('reply.choices')));
    this.sendAction('isReplyReadyUpdated', this.get('is_reply_ready'));
    return this.updateSelections();
  }.on('init'),
  //
  // Observer function
  //
  onCheckedChanged: function () {
    var checked, choices, old_choices;
    if (this.get('dataset.is_multiple_choice')) {
      return;
    }
    old_choices = this.get('reply.choices');
    checked = this.get('checked');
    choices = old_choices.map(function (a, index) {
      return index === checked;
    });
    if (!_.isEqual(old_choices, choices)) {
      this.set('reply', {choices: choices});
      this.sendAction('replyUpdated', this.get('reply'));
      this.set('is_reply_ready', this.get('dataset.is_multiple_choice') || _.some(choices));
      return this.sendAction('isReplyReadyUpdated', this.get('is_reply_ready'));
    }
  }.observes('checked'),
  selectionsObserver: function () {
    return this.updateSelections();
  }.observes('dataset.options', 'reply.choices.@each', 'feedback.options_feedback'),
  //
  // Methods
  //
  updateSelections: function () {
    var new_selections, old_selections;
    old_selections = this.get('selections');
    new_selections = _(this.get('dataset.options')).zip(this.get('reply.choices')).map(function (arg) {
      var is_checked, text;
      text = arg[0], is_checked = arg[1];
      return Em.Object.create({
        text: text,
        is_checked: is_checked
      });
    });
    if (!_.isEqual(old_selections, new_selections)) {
      if (old_selections.length === 0) {
        this.set('selections', new_selections);
      } else {
        old_selections.forEach(function (option, index) {
          option.set('is_checked', new_selections[index].is_checked);
        });
      }
    }
    if (this.get('feedback.options_feedback')) {
      this.get('selections').forEach((option, index) => {
        option.set('feedback', this.get('feedback.options_feedback.' + index));
      })
    }
  },
  //
  // Actions
  //
  actions: {
    optionChecked: function (index) {
      var choices, old_choices, value;
      if (!this.get('dataset.is_multiple_choice')) {
        return;
      }
      value = this.$('[data-index=' + index + ']')[0].checked;
      old_choices = this.get('reply.choices');
      choices = old_choices.map(function (a, ii) {
        if (index === ii) {
          return value;
        } else {
          return a;
        }
      });
      if (!_.isEqual(old_choices, choices)) {
        this.set('reply', {choices: choices});
        this.sendAction('replyUpdated', this.get('reply'));
      }
      return false;
    }
  }
});
