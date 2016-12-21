export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  active_slot: null,
  //
  // Event handlers
  //
  initTable: function () {
    return $('#periodic-table td.element dl').click(event => {
      var element_symbol;
      if (this.get('active_slot')) {
        element_symbol = $(event.currentTarget).children('[itemprop="symbol"]').val();
        return this.get('active_slot').val(element_symbol).change();
      }
    });
  }.on('didInsertElement'),
  setInitial: function () {
    var i, slot;
    if (this.get('reply') == null) {
      this.set('reply', {
        slots: function () {
          var j, len, ref, results;
          ref = this.get('dataset.template');
          results = [];
          for (j = 0, len = ref.length; j < len; j++) {
            slot = ref[j];
            results.push({
              normal: '',
              sub: '',
              sup: ''
            });
          }
          return results;
        }.call(this)
      });
      this.sendAction('replyUpdated', this.get('reply'));
    }
    return this.set('slots', function () {
      var j, len, ref, ref1, ref2, results;
      ref = this.get('reply.slots');
      results = [];
      for (i = j = 0, len = ref.length; j < len; i = ++j) {
        slot = ref[i];
        results.push({
          value: slot,
          is_subsup: this.get('dataset.template.' + i) !== 'normal',
          is_sub: (ref1 = this.get('dataset.template.' + i)) === 'subsup' || ref1 === 'sub',
          is_sup: (ref2 = this.get('dataset.template.' + i)) === 'subsup' || ref2 === 'sup'
        });
      }
      return results;
    }.call(this));
  }.on('init'),
  //
  // Actions
  //
  actions: {
    selectActiveSlot: function () {
      var active_slot;
      if (this.get('active_slot')) {
        this.get('active_slot').removeClass('chemical-template__slot_active');
      }
      active_slot = $(document.activeElement);
      active_slot.addClass('chemical-template__slot_active');
      return this.set('active_slot', active_slot);
    },
    toggleTable: function () {
      return this.toggleProperty('is_table_shown');
    }
  }
});
