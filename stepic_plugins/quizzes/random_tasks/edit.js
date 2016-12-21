export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      task: '',
      solve: '',
      max_error: '0',
      ranges: [],
      combinations: 0
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Observer function
  //
  onRangesChanged: function () {
    var combinations, i, len, num_from, num_step, num_to, range, ref;
    combinations = 1;
    ref = this.get('source.ranges');
    for (i = 0, len = ref.length; i < len; i++) {
      range = ref[i];
      num_from = parseFloat(range.num_from);
      num_to = parseFloat(range.num_to);
      num_step = parseFloat(range.num_step);
      combinations *= Math.abs((num_to - num_from) / num_step);
    }
    return this.set('source.combinations', combinations);
  }.observes('source.ranges.@each.num_from', 'source.ranges.@each.num_to', 'source.ranges.@each.num_step'),
  setRanges: function () {
    var i, index, is_in_ranges, j, k, len, len1, len2, range, ref, ref1, task, temp_ranges, text, word;
    temp_ranges = [];
    index = {};
    task = [];
    ref = this.get('source.task').split(/[^a-zA-Z0-9_\\]/);
    for (i = 0, len = ref.length; i < len; i++) {
      text = ref[i];
      if (!(text in index)) {
        index[text] = true;
        task.push(text);
      }
    }
    for (j = 0, len1 = task.length; j < len1; j++) {
      word = task[j];
      if (word.length > 1) {
        if (word[0] === '\\' && word[1] !== '\\') {
          is_in_ranges = false;
          ref1 = this.get('source.ranges');
          for (k = 0, len2 = ref1.length; k < len2; k++) {
            range = ref1[k];
            if (range.variable === word.slice(1)) {
              is_in_ranges = true;
              temp_ranges.push(range);
              break;
            }
          }
          if (!is_in_ranges) {
            temp_ranges.push({
              variable: word.slice(1),
              num_from: '1',
              num_to: '2',
              num_step: '1'
            });
          }
        }
      }
    }
    return this.set('source.ranges', temp_ranges);
  }.observes('source.task')
});
