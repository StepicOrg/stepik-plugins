export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  min_height: 0,
  //
  // Event handlers
  //
  setInitial: function () {
    var N, index, initial_ordering;
    if (!this.get('reply.ordering')) {
      N = this.get('dataset.pairs.length');
      initial_ordering = Array.apply(null, {length: N}).map(Number.call, Number);
      this.set('reply', {ordering: initial_ordering});
      this.sendAction('replyUpdated', this.get('reply'));
    }
    this.set('options', function () {
      var i, len, ref, results;
      ref = this.get('reply.ordering');
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        index = ref[i];
        results.push({
          index: index,
          second: this.get('dataset.pairs')[index].second
        });
      }
      return results;
    }.call(this));
    $(window).on('resize', () => {
      return this.resizeItems(true);
    });
    return this.resizeItems(false);
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
    this.sendAction('replyUpdated', this.get('reply'));
    return this.resizeItems(false);
  }.observes('options'),
  //
  // Methods
  //
  resizeItems: function (hard_reset) {
    if (this._state === 'destroying') {
      return;
    }
    if (hard_reset) {
      this.set('min_height', 0);
    }
    return Em.run.next(() => {
      var height;
      if (this._state !== 'inDOM') {
        return;
      }
      height = 0;
      this.$('.sortable-item__inner-box').each(function () {
        return height = Math.max(height, $(this).outerHeight());
      });
      return this.set('min_height', height);
    });
  }
});
