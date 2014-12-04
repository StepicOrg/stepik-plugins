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
    langs: (function() {
      return _.keys(this.get('content.options.code_templates'));
    }).property('content'),
    is_lang_selectable: (function() {
      return !(this.get('user_code') || this.get('user_lang'));
    }).property('langs', 'user_lang'),
    code_template: (function() {
      if (this.get('user_lang')) {
        return this.get('content.options.code_templates')[this.get('user_lang')];
      }
    }).property('user_lang'),
    _set_initial_language: (function() {
      if (this.get('content') && this.get('langs.length') === 1) {
        return this.set('user_lang', this.get('langs.firstObject'));
      }
    }).observes('langs').on('init'),
    _set_initial_code: (function() {
      var initial_code;
      if (!this.get('user_code') && this.get('user_lang')) {
        initial_code = this.get('previous_reply.language') === this.get('user_lang') ? this.get('previous_reply.code') : this.get('code_template');
        return this.set('user_code', initial_code);
      }
    }).observes('user_lang'),
    onLangSelected: (function() {
      return this.set('is_reply_ready', !this.get('is_lang_selectable'));
    }).observes('is_lang_selectable').on('init'),
    actions: {
      setLang: function(lang) {
        return this.set('user_lang', lang);
      }
    }
  });

}).call(this);
