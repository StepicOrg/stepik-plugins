import * as utils from 'stepic/utils';
import { iscrollConfig } from 'stepic/utils';

export default Em.Component.extend({
  //
  // Computed property functions
  //
  choice_type: function (key, value) {
    if (arguments.length > 1) {
      this.set('source.options.is_checkbox', value === 'checkbox');
    }
    if (this.get('source.options.is_checkbox')) {
      return 'checkbox';
    } else {
      return 'radio';
    }
  }.property('source.options.is_checkbox'),
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
    var column, default_source, name_columns;
    name_columns = [
      {name: 'First column'},
      {name: 'Second column'},
      {name: 'Third column'}
    ];
    default_source = {
      rows: [
        {
          name: 'First row',
          columns: function () {
            var i, len, results;
            results = [];
            for (i = 0, len = name_columns.length; i < len; i++) {
              column = name_columns[i];
              results.push({choice: false});
            }
            return results;
          }()
        },
        {
          name: 'Second row',
          columns: function () {
            var i, len, results;
            results = [];
            for (i = 0, len = name_columns.length; i < len; i++) {
              column = name_columns[i];
              results.push({choice: false});
            }
            return results;
          }()
        },
        {
          name: 'Third row',
          columns: function () {
            var i, len, results;
            results = [];
            for (i = 0, len = name_columns.length; i < len; i++) {
              column = name_columns[i];
              results.push({choice: false});
            }
            return results;
          }()
        }
      ],
      options: {
        is_checkbox: false,
        is_randomize_rows: false,
        is_randomize_columns: false,
        sample_size: -1
      },
      columns: name_columns,
      description: 'Rows: ',
      is_always_correct: false
    };
    this.set('source', this.get('source') || default_source);
    this.sendAction('sourceUpdated', this.get('source'));
    return this.set('choice_type_options', [
      {
        value: 'radio',
        label: 'Single choice per row'
      },
      {
        value: 'checkbox',
        label: 'Multiple choices per row'
      }
    ]);
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
  // Actions
  //
  actions: {
    addColumn: function () {
      var i, len, new_columns, new_rows, row;
      new_rows = this.get('source.rows').slice();
      new_columns = this.get('source.columns').slice();
      new_columns.push({name: 'New column'});
      for (i = 0, len = new_rows.length; i < len; i++) {
        row = new_rows[i];
        row.columns.push({choice: false});
      }
      this.set('source.rows', new_rows);
      return this.set('source.columns', new_columns);
    },
    deleteColumn: function () {
      var i, len, new_columns, new_rows, row;
      if (this.get('source.columns').length > 1) {
        new_rows = this.get('source.rows').slice();
        new_columns = this.get('source.columns').slice();
        new_columns.pop();
        for (i = 0, len = new_rows.length; i < len; i++) {
          row = new_rows[i];
          row.columns.pop();
        }
        this.set('source.rows', new_rows);
        return this.set('source.columns', new_columns);
      }
    },
    addRow: function () {
      var column, new_rows;
      new_rows = this.get('source.rows').slice();
      new_rows.push({
        name: 'Next row',
        columns: function () {
          var i, len, ref, results;
          ref = this.get('source.columns');
          results = [];
          for (i = 0, len = ref.length; i < len; i++) {
            column = ref[i];
            results.push({choice: false});
          }
          return results;
        }.call(this)
      });
      return this.set('source.rows', new_rows);
    },
    deleteRow: function () {
      var new_rows;
      if (this.get('source.rows').length > 1) {
        new_rows = this.get('source.rows').slice();
        new_rows.pop();
        return this.set('source.rows', new_rows);
      }
    }
  }
});
