(function() {
  App.ChoiceQuizEditorComponent = Em.Component.extend({
    init: function() {
      var default_source;
      this._super();
      default_source = {
        is_multiple_choice: false,
        is_always_correct: false,
        sample_size: "3",
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
      this.set('source.sample_size', this.get('source.sample_size').toString());
      return this.get('source');
    },
    didInsertElement: function() {
      return this.setBindings();
    },
    setBindings: function() {
      var component, dragSource, options;
      dragSource = null;
      component = this;
      options = this.$('.choice-option');
      return options.off().on('dragstart', function(e) {
        dragSource = this;
        return e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
      }).on('dragover', function(e) {
        return e.preventDefault();
      }).on('drop', function(e) {
        var new_options;
        if (options.index(dragSource) > options.index(this)) {
          $(this).before(dragSource);
        } else {
          $(this).after(dragSource);
        }
        new_options = [];
        component.$('.choice-option').each(function(i, v) {
          return new_options.push({
            text: $(v).find('.text').val(),
            is_correct: $(v).find('.is_correct').is(':checked')
          });
        });
        component.set('source.options', new_options);
        return Em.run.next(function() {
          return component.setBindings();
        });
      });
    },
    actions: {
      addOption: function() {
        this.get('source.options').pushObject({
          is_correct: false,
          text: ''
        });
        return Em.run.next((function(_this) {
          return function() {
            return _this.setBindings();
          };
        })(this));
      },
      removeOption: function(option) {
        this.set('source.options', this.get('source.options').without(option));
        return Em.run.next((function(_this) {
          return function() {
            return _this.setBindings();
          };
        })(this));
      }
    }
  });

}).call(this);
