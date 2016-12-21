export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var N, index, initial_ordering;
    if (!this.get('reply.ordering')) {
      N = this.get('dataset.options.length');
      initial_ordering = Array.apply(null, {length: N}).map(Number.call, Number);
      this.set('reply', {ordering: initial_ordering});
      this.sendAction('replyUpdated', this.get('reply'));
    }
    return this.set('options', function () {
      var i, len, ref, results;
      ref = this.get('reply.ordering');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        index = ref[i];
        results.push({
          index: index,
          text: this.get('dataset.options')[index]
        });
      }
      return results;
    }.call(this));
  }.on('init'),
  //
  // Observer function
  //
  onOptionsChanged: function () {
    var option;
    this.set('reply', {
      ordering: function () {
        var i, len, ref, results;
        ref = this.get('options');
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          option = ref[i];
          results.push(option.index);
        }
        return results;
      }.call(this)
    });
    return this.sendAction('replyUpdated', this.get('reply'));
  }.observes('options')
});
