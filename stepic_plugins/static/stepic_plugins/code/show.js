(function() {
  App.CodeQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        return this.set('reply', {
          code: '',
          language: null
        });
      }
    },
    user_langBinding: 'reply.language',
    user_codeBinding: 'reply.code',
    _apply_template: (function() {
      if (!this.get('user_code') && this.get('user_lang')) {
        return this.set('user_code', this.get('code_template'));
      }
    }).observes('user_lang'),
    langs: (function() {
      return _.keys(this.get('content.code_templates'));
    }).property('content'),
    is_lang_selectable: (function() {
      return !(this.get('user_code') || this.get('user_lang'));
    }).property('langs', 'user_lang'),
    code_template: (function() {
      if (this.get('user_lang')) {
        return this.get('content.code_templates')[this.get('user_lang')];
      }
    }).property('user_lang'),
    actions: {
      setLang: function(lang) {
        return this.set('user_lang', lang);
      }
    }
  });

}).call(this);
