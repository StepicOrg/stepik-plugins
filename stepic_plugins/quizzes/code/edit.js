import * as utils from 'stepic/utils';
import 'stepic/app';
import CodeEditorView from 'stepic/views/code-editor';

export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  CodeEditorView: CodeEditorView,
  DEFAULT_MEMORY_LIMIT_FACTORS: {},
  DEFAULT_TIME_LIMIT_FACTORS: {
    python3: 3,
    haskell: 2,
    'haskell 7.10': 2,
    'haskell 8.0': 2,
    java: 1.5,
    java8: 1.5,
    octave: 2.5,
    rust: 2.5,
    r: 1.5,
    ruby: 3,
    clojure: 2,
    'mono c#': 1.5,
    javascript: 3,
    scala: 1.5
  },
  LANGUAGES: [
    'python3',
    'c',
    'c++',
    'c++11',
    'haskell',
    'haskell 7.10',
    'haskell 8.0',
    'java',
    'java8',
    'octave',
    'asm32',
    'asm64',
    'shell',
    'rust',
    'r',
    'ruby',
    'clojure',
    'mono c#',
    'javascript',
    'scala'
  ],
  limits: [],
  //
  // Simple computed properties
  //
  is_limits_table_displayed: Em.computed.or('source.is_time_limit_scaled', 'source.is_memory_limit_scaled'),
  //
  // Event handlers
  //
  limitsObserver: function () {
    var current_limits, i, language, len, limits, manual_memory, manual_time, memory_factor, memory_limit, ml, new_limits, ref, time_factor, time_limit, tl;
    time_limit = this.get('source.execution_time_limit');
    memory_limit = this.get('source.execution_memory_limit');
    limits = [];
    ref = this.get('LANGUAGES');
    for (i = 0, len = ref.length; i < len; i++) {
      language = ref[i];
      time_factor = this.get('DEFAULT_TIME_LIMIT_FACTORS.')[language] || 1;
      memory_factor = this.get('DEFAULT_MEMORY_LIMIT_FACTORS')[language] || 1;
      tl = !this.get('source.is_time_limit_scaled') ? time_limit : Math.round(time_limit * time_factor);
      ml = !this.get('source.is_memory_limit_scaled') ? memory_limit : Math.round(memory_limit * memory_factor);
      manual_time = this.get('source.manual_time_limits').filterBy('language', language)[0];
      manual_memory = this.get('source.manual_memory_limits').filterBy('language', language)[0];
      limits.push({
        language: language,
        time: tl,
        memory: ml,
        time_factor: time_factor,
        memory_factor: memory_factor,
        is_time_correct: tl > 0,
        is_memory_correct: ml > 0,
        is_manual_time: !!manual_time,
        is_manual_memory: !!manual_memory,
        manual_time: manual_time ? manual_time.time : tl,
        manual_memory: manual_memory ? manual_memory.memory : ml
      });
    }
    current_limits = utils.deepCopy(this.get('limits'));
    new_limits = utils.deepCopy(limits);
    if (!utils.objectsEqual(current_limits, new_limits)) {
      return this.set('limits', limits);
    }
  }.observes('source.execution_time_limit', 'source.execution_memory_limit', 'source.is_time_limit_scaled', 'source.is_memory_limit_scaled', 'source.manual_time_limits', 'source.manual_memory_limits').on('init'),
  setInitial: function () {
    var default_source;
    default_source = {
      code: '#This is sample code challenge\nimport random\n\ndef generate():\n    num_tests = 10\n    tests = []\n    for test in range(num_tests):\n        a = random.randrange(10)\n        b = random.randrange(10)\n        test_case = "{} {}\\n".format(a, b)\n        tests.append(test_case)\n    return tests\n\n\ndef solve(dataset):\n    a, b = dataset.split()\n    return str(int(a)+int(b))\n\n\ndef check(reply, clue):\n    return int(reply) == int(clue)',
      execution_time_limit: 5,
      execution_memory_limit: 256,
      samples_count: 1,
      templates_data: '',
      is_time_limit_scaled: true,
      is_memory_limit_scaled: true,
      manual_time_limits: [],
      manual_memory_limits: [],
      test_archive: []
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Observer function
  //
  onMemoryLimitChanged: function () {
    var l;
    return this.set('source.manual_memory_limits', function () {
      var i, len, ref, results;
      ref = this.get('limits');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        l = ref[i];
        if (l.is_manual_memory) {
          results.push({
            language: l.language,
            memory: l.manual_memory
          });
        }
      }
      return results;
    }.call(this));
  }.observes('limits.@each.manual_memory', 'limits.@each.is_manual_memory'),
  onTimeLimitChanged: function () {
    var l;
    return this.set('source.manual_time_limits', function () {
      var i, len, ref, results;
      ref = this.get('limits');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        l = ref[i];
        if (l.is_manual_time) {
          results.push({
            language: l.language,
            time: l.manual_time
          });
        }
      }
      return results;
    }.call(this));
  }.observes('limits.@each.manual_time', 'limits.@each.is_manual_time'),
  //
  // Actions
  //
  actions: {
    toggleManualLimit: function (language, limit_type) {
      var idx;
      idx = this.get('LANGUAGES').indexOf(language);
      return this.toggleProperty('limits.' + idx + '.is_manual_' + limit_type);
    }
  }
});
