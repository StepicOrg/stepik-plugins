(function() {
  App.CodeQuizComponent = Em.Component.extend({
    init: function() {
      this._super();
      if (this.get('reply') == null) {
        this.set('reply', {
          code: '',
          language: null
        });
        if (!this.get('is_multiple_langs')) {
          return this.set('user_lang', this.get('langs.firstObject'));
        }
      }
    },
    user_lang: Em.computed.alias('reply.language'),
    user_code: Em.computed.alias('reply.code'),
    is_multiple_langs: Em.computed.gt('langs.length', 1),
    file_value: null,
    setLangVisually: (function() {
      if (this.get('user_lang') && this.get('is_multiple_langs')) {
        return this.$(".lang-selector").val(this.get('user_lang'));
      }
    }).on('didInsertElement'),
    langs: (function() {
      return _.keys(this.get('content.options.code_templates'));
    }).property('content'),
    code_template: (function() {
      if (this.get('user_lang')) {
        return this.get('content.options.code_templates')[this.get('user_lang')];
      }
    }).property('user_lang'),
    initial_code: (function() {
      if (this.get('previous_reply.language') === this.get('user_lang')) {
        return this.get('previous_reply.code');
      } else {
        return this.get('code_template');
      }
    }).property('user_lang'),
    uploadFile: (function() {
      var file, reader;
      file = this.$('input[type="file"]')[0].files[0];
      if (!file) {
        return;
      }
      reader = new FileReader();
      reader.onload = (function(_this) {
        return function() {
          return _this.set('reply.code', reader.result);
        };
      })(this);
      return reader.readAsText(file.slice());
    }).observes('file_value'),
    setInitialCode: (function(forced) {
      if (forced == null) {
        forced = false;
      }
      if (!this.get('user_code') && this.get('user_lang')) {
        return this.set('user_code', this.get('initial_code'));
      }
    }).observes('user_lang'),
    _set_initial_code: (function() {
      var initial_code;
      if (!this.get('user_code') && this.get('user_lang')) {
        initial_code = this.get('previous_reply.language') === this.get('user_lang') ? this.get('previous_reply.code') : this.get('code_template');
        return this.set('user_code', initial_code);
      }
    }).observes('user_lang'),
    onLangSelected: (function() {
      return this.set('is_reply_ready', !!this.get('user_lang'));
    }).observes('user_lang').on('init'),
    actions: {
      setLang: function() {
        var lang;
        lang = this.$('.lang-selector').val();
        if ((this.get('initial_code') === this.get('user_code')) || !this.get('user_code') || confirm('This will erase your changes!')) {
          this.set('user_lang', lang);
          return this.set('user_code', this.get('initial_code'));
        }
      }
    }
  });

}).call(this);
