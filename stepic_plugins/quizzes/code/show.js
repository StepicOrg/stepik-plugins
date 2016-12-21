import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  LANGUAGE_LABELS: {
    python3: "Python 3",
    'c': "C",
    'c++': "C++",
    'c++11': "C++11",
    haskell: "Haskell (ghc 7.8)",
    'haskell 7.10': "Haskell (ghc 7.10)",
    'haskell 8.0': "Haskell (ghc 8.0)",
    java: "Java 7",
    java8: "Java 8",
    octave: "Octave",
    asm32: "ASM32",
    asm64: "ASM64",
    shell: "Shell",
    rust: "Rust",
    r: "R",
    ruby: "Ruby",
    clojure: "Clojure",
    'mono c#': "C#",
    javascript: "JavaScript",
    scala: "Scala"
  },
  //
  // Property aliases
  //
  user_code: Em.computed.alias('reply.code'),
  user_lang: Em.computed.alias('reply.language'),
  //
  // Simple computed properties
  //
  is_multiple_langs: Em.computed.gt('langs.length', 1),
  CodeEditorView: CodeEditorView,
  //
  // Computed property functions
  //
  code_template: function () {
    if (this.get('user_lang')) {
      return this.get('content.options.code_templates')[this.get('user_lang')];
    }
  }.property('user_lang'),
  initial_code: function () {
    if (this.get('previous_reply.language') === this.get('user_lang')) {
      return this.get('previous_reply.code');
    } else {
      return this.get('code_template');
    }
  }.property('user_lang'),
  langs: function () {
    return Object.keys(this.get('content.options.code_templates')).map(lang => (
        {id: lang, label: this.get('LANGUAGE_LABELS')[lang]}
      )).sortBy('label');
  }.property('content'),
  //
  // Event handlers
  //
  onLangSelected: function () {
    var user_lang = this.get('user_lang');
    this.set('is_reply_ready', !!user_lang);
    this.sendAction('isReplyReadyUpdated', !!user_lang);
    const lang_limits = this.get('content.options.limits')[user_lang];
    this.set('limits', {
      // lang_limits can be undefined if an old submission is selected that was
      // submitted using a language that doesn't exist in this step any more.
      time: lang_limits ? lang_limits.time : undefined,
      memory: lang_limits ? lang_limits.memory : undefined
    });
  }.observes('user_lang').on('init'),
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {
        code: '',
        language: null
      });
      this.sendAction('replyUpdated', this.get('reply'));
      this.sendAction('isReplyReadyUpdated', false);
      if (!this.get('is_multiple_langs')) {
        this.set('user_lang', this.get('langs.firstObject.id'));
        this.setInitialCode();
      }
    }
    return this.set('previous_reply', {
      code: this.get('reply').code,
      language: this.get('reply').language
    });
  }.on('init'),
  //
  // Observer function
  //
  setInitialCode: function (forced) {
    if (forced == null) {
      forced = false;
    }
    if (!this.get('user_code') && this.get('user_lang')) {
      return this.set('user_code', this.get('initial_code'));
    }
  }.observes('user_lang'),
  setLangVisually: function () {
    return Em.run.schedule('afterRender', () => {
      if (this.get('user_lang') && this.get('is_multiple_langs')) {
        return this.$('.lang-selector').val(this.get('user_lang'));
      }
    });
  }.on('didInsertElement').observes('disabled'),
  //
  // Methods
  //
  uploadFile: function () {
    var file, reader;
    file = this.$('input[type="file"]')[0].files[0];
    if (!file) {
      return;
    }
    reader = new FileReader();
    reader.onload = () => {
      return this.set('reply.code', reader.result);
    };
    return reader.readAsText(file.slice());
  },
  //
  // Actions
  //
  actions: {
    startUpload: function () {
      return this.uploadFile();
    },
    setLang: function () {
      var lang;
      lang = this.$('.lang-selector').val();
      if (this.get('initial_code') === this.get('user_code') || !this.get('user_code') || confirm('This will erase your changes!')) {
        this.set('user_lang', lang);
        return this.set('user_code', this.get('initial_code'));
      }
    }
  }
});
