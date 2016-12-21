import * as utils from 'stepic/utils';
import { iscrollConfig } from 'stepic/utils';

export default Em.Component.extend({
  //
  // Event handlers
  //
  destroyIscroll: function () {
    var ref;
    if ((ref = this.get('iscroll')) != null) {
      ref.destroy();
    }
    return clearInterval(this.get('interval_id'));
  }.on('willDestroyElement'),
  setInitial: function () {
    var column, default_reply, row;
    default_reply = {
      choices: function () {
        var i, len, ref, results;
        ref = this.get('dataset.rows');
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          row = ref[i];
          results.push({
            name_row: row,
            columns: function () {
              var j, len1, ref1, results1;
              ref1 = this.get('dataset.columns');
              results1 = [];
              for (j = 0, len1 = ref1.length; j < len1; j++) {
                column = ref1[j];
                results1.push({
                  name: column,
                  answer: false
                });
              }
              return results1;
            }.call(this)
          });
        }
        return results;
      }.call(this)
    };
    this.set('reply', this.get('reply') || default_reply);
    return this.sendAction('replyUpdated', this.get('reply'));
  }.on('init'),
  setIscroll: function () {
    const deltaConfig = {
      scrollX: true,
      scrollY: false,
      probeType: 3
    };
    const config = Object.assign({}, iscrollConfig, deltaConfig);
    if (this.get('iscroll')) {
      this.get('iscroll').destroy();
      this.set('iscroll', null);
    }
    clearInterval(this.get('interval_id'));
    var interval_id, iscroll;
    if (this.get('isDestroying')) {
      return;
    }
    iscroll = new IScroll(this.$('.table-quiz').get(0), config);
    this.set('iscroll', iscroll);
    interval_id = setInterval(function () {
      return iscroll !== null ? iscroll.refresh() : void 0;
    }, 300);
    return this.set('interval_id', interval_id);
  }.on('didInsertElement'),
  //
  // Other
  //
  picker_view: Em.computed('dataset.is_checkbox', function () {
    if (this.get('dataset.is_checkbox')) {
      return Em.Checkbox;
    } else {
      return Em.RadioButton;
    }
  })
});
