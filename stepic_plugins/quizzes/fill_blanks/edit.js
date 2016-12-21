export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  blank_types: [
    {
      label: 'Text input',
      value: 'input'
    },
    {
      label: 'Choice',
      value: 'select'
    }
  ],
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      components: [
        {
          type: 'text',
          text: '2 + 2 =',
          options: []
        },
        {
          type: 'input',
          text: '',
          options: [{
              text: '4',
              is_correct: true
            }]
        }
      ],
      is_case_sensitive: false
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Observer function
  //
  setSelectBlank: function () {
    var component, i, len, option, ref, results;
    ref = this.get('source.components');
    results = [];
    for (i = 0, len = ref.length; i < len; i++) {
      component = ref[i];
      if (component.type === 'input') {
        results.push(function () {
          var j, len1, ref1, results1;
          ref1 = component.options;
          results1 = [];
          for (j = 0, len1 = ref1.length; j < len1; j++) {
            option = ref1[j];
            if (!option.is_correct) {
              results1.push(Em.set(option, 'is_correct', true));
            } else {
              results1.push(void 0);
            }
          }
          return results1;
        }());
      } else {
        results.push(void 0);
      }
    }
    return results;
  }.observes('source.components.@each.type'),
  //
  // Actions
  //
  actions: {
    addText: function () {
      return this.get('source.components').pushObject({
        type: 'text',
        text: '',
        options: []
      });
    },
    addBlank: function () {
      return this.get('source.components').pushObject({
        type: 'input',
        text: '',
        options: []
      });
    },
    addOption: function (options_list, is_correct) {
      return options_list.pushObject({
        text: '',
        is_correct: is_correct
      });
    },
    removeComponent: function (component) {
      return this.set('source.components', this.get('source.components').without(component));
    },
    removeOption: function (option, component) {
      return Em.set(component, 'options', component.options.without(option));
    }
  }
});
