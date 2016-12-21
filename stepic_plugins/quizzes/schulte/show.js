export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  DEFAULT_NONGRID_CELL_SIZE: 60,
  DEFAULT_NONGRID_FONT_SIZE: 1.5,
  MAX_COLOR_COMPONENT_SHIFT: 120,
  MAX_FONT_SIZE: 2.5,
  MIN_FONT_SIZE: 0.9,
  next_cell_id: 0,
  RANDOM_COLOR_SATURATION: 1,
  RANDOM_COLOR_VALUE: 0.9,
  //
  // Event handlers
  //
  initTable: function () {
    var cell, cell_elem, j, len, min_cell_height, min_table_size, quiz_width, ref, table_size, table_size_px;
    if (this.get('disabled')) {
      return;
    }
    if (!this.get('dataset.is_grid')) {
      table_size = this.get('dataset.table_size');
      quiz_width = $('.schulte-quiz__wrapper').width();
      min_cell_height = $('[data-cell-id=0]').height() / this.get('cells_sequence.0.font_size') * this.DEFAULT_NONGRID_FONT_SIZE;
      min_table_size = Math.floor(table_size * min_cell_height * 1.7);
      table_size_px = Math.min(table_size * this.DEFAULT_NONGRID_CELL_SIZE, quiz_width);
      table_size_px = Math.max(table_size_px, min_table_size);
      this.set('table_size_px', table_size_px);
      $('.schulte-quiz__table').width(table_size_px).height(table_size_px);
      ref = this.get('cells_sequence');
      for (j = 0, len = ref.length; j < len; j++) {
        cell = ref[j];
        cell_elem = $('[data-cell-id=' + cell.id + ']');
        cell.elem = cell_elem;
        cell.width = cell_elem.width();
        cell.height = cell_elem.height();
      }
      this.arrangeCells();
    }
    $('[data-cell-id]').click(event => {
      var cell_id;
      cell = $(event.currentTarget);
      cell_id = cell.data('cell-id');
      if (this.get('next_cell_id') === cell_id) {
        this.animateCell(true, cell);
        return this.set('next_cell_id', cell_id + 1);
      } else {
        return this.animateCell(false, cell);
      }
    });
    this.set('start_time', new Date());
    return this.timeTick();
  }.on('didInsertElement'),
  setInitial: function () {
    var black_length, black_sequence, cell, cellColor, cells_sequence, i, j, k, l, len, len1, n, red_length, red_sequence, ref, shuffled_sequence, table_size;
    if (this.get('reply') == null) {
      this.set('reply', {
        solved: false,
        time_seconds: 0
      });
      this.sendAction('replyUpdated', this.get('reply'));
    }
    if (this.get('disabled')) {
      return;
    }
    table_size = this.get('dataset.table_size');
    if (!this.get('dataset.is_gorbov_table')) {
      cellColor = () => {
        if (this.get('dataset.is_color_randomized')) {
          return this.randomColor();
        } else {
          return '#000000';
        }
      };
      cells_sequence = function () {
        var j, ref, results;
        results = [];
        for (n = j = 1, ref = table_size * table_size; 1 <= ref ? j <= ref : j >= ref; n = 1 <= ref ? ++j : --j) {
          results.push({
            number: n,
            color: cellColor()
          });
        }
        return results;
      }();
    } else {
      cellColor = base_color => {
        if (this.get('dataset.is_color_randomized')) {
          return this.shiftColor(base_color, this.MAX_COLOR_COMPONENT_SHIFT);
        } else {
          return base_color;
        }
      };
      black_length = Math.round(table_size * table_size / 2);
      black_sequence = function () {
        var j, ref, results;
        results = [];
        for (n = j = 1, ref = black_length; 1 <= ref ? j <= ref : j >= ref; n = 1 <= ref ? ++j : --j) {
          results.push({
            number: n,
            color: cellColor('#000000')
          });
        }
        return results;
      }();
      red_length = Math.floor(table_size * table_size / 2);
      red_sequence = function () {
        var j, ref, results;
        results = [];
        for (n = j = ref = red_length; ref <= 1 ? j <= 1 : j >= 1; n = ref <= 1 ? ++j : --j) {
          results.push({
            number: n,
            color: cellColor('#ff0000')
          });
        }
        return results;
      }();
      cells_sequence = _.flatten(_.zip(black_sequence, red_sequence)).slice(0, black_length + red_length);
    }
    for (i = j = 0, ref = cells_sequence.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
      cells_sequence[i].id = i;
    }
    if (this.get('dataset.is_grid')) {
      shuffled_sequence = _.shuffle(cells_sequence);
      this.set('table', function () {
        var k, ref1, results;
        results = [];
        for (i = k = 0, ref1 = table_size - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; i = 0 <= ref1 ? ++k : --k) {
          results.push(shuffled_sequence.slice(i * table_size, (i + 1) * table_size));
        }
        return results;
      }());
      if (table_size > 5) {
        this.set('is_cell_small', true);
      }
    } else {
      if (this.get('dataset.is_font_randomized')) {
        for (k = 0, len = cells_sequence.length; k < len; k++) {
          cell = cells_sequence[k];
          cell.font_size = Math.round((Math.random() * (this.MAX_FONT_SIZE - this.MIN_FONT_SIZE) + this.MIN_FONT_SIZE) * 10) / 10;
        }
      } else {
        for (l = 0, len1 = cells_sequence.length; l < len1; l++) {
          cell = cells_sequence[l];
          cell.font_size = this.DEFAULT_NONGRID_FONT_SIZE;
        }
      }
    }
    this.set('cells_sequence', cells_sequence);
    return this.set('next_cell', cells_sequence[0]);
  }.on('init'),
  //
  // Observer function
  //
  nextCellClicked: function () {
    var next_cell_id;
    next_cell_id = this.get('next_cell_id');
    if (next_cell_id >= this.get('cells_sequence').length) {
      this.set('reply.solved', true);
      return this.set('next_cell', null);
    } else {
      return this.set('next_cell', this.get('cells_sequence.' + next_cell_id));
    }
  }.observes('next_cell_id'),
  //
  // Methods
  //
  animateCell: function (answer, cell) {
    var effect_class;
    effect_class = answer ? 'schulte-quiz__table-cell_correct' : 'schulte-quiz__table-cell_wrong';
    cell.addClass(effect_class);
    return setTimeout(function () {
      return cell.removeClass(effect_class);
    }, 300);
  },
  arrangeCells: function () {
    var results, tryArrangeCells;
    tryArrangeCells = () => {
      var cell, intersects, j, k, len, ref, retries;
      ref = this.get('cells_sequence');
      for (j = 0, len = ref.length; j < len; j++) {
        cell = ref[j];
        for (retries = k = 1000; k >= 0; retries = k += -1) {
          cell.top = Math.floor(Math.random() * (this.get('table_size_px') - cell.height));
          cell.left = Math.floor(Math.random() * (this.get('table_size_px') - cell.width));
          intersects = _.any(this.get('cells_sequence').slice(0, cell.id), c => {
            return this.isIntersection(c, cell);
          });
          if (!intersects) {
            cell.elem.css({
              top: cell.top,
              left: cell.left
            });
            break;
          }
        }
        if (retries < 0) {
          return false;
        }
      }
      return true;
    };
    results = [];
    while (!tryArrangeCells()) {
      results.push(console.log('Retry to arrange table'));
    }
    return results;
  },
  hsvToRgb: function (h, s, v) {
    var b, f, g, i, p, q, r, ref, ref1, ref2, ref3, ref4, ref5, t;
    i = Math.floor(h * 6);
    f = h * 6 - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i % 6) {
    case 0:
      ref = [
        v,
        t,
        p
      ], r = ref[0], g = ref[1], b = ref[2];
      break;
    case 1:
      ref1 = [
        q,
        v,
        p
      ], r = ref1[0], g = ref1[1], b = ref1[2];
      break;
    case 2:
      ref2 = [
        p,
        v,
        t
      ], r = ref2[0], g = ref2[1], b = ref2[2];
      break;
    case 3:
      ref3 = [
        p,
        q,
        v
      ], r = ref3[0], g = ref3[1], b = ref3[2];
      break;
    case 4:
      ref4 = [
        t,
        p,
        v
      ], r = ref4[0], g = ref4[1], b = ref4[2];
      break;
    case 5:
      ref5 = [
        v,
        p,
        q
      ], r = ref5[0], g = ref5[1], b = ref5[2];
    }
    return [
      Math.round(r * 255),
      Math.round(g * 255),
      Math.round(b * 255)
    ];
  },
  isIntersection: function (cell_a, cell_b) {
    return !(cell_a.left > cell_b.left + cell_b.width || cell_a.left + cell_a.width < cell_b.left || cell_a.top > cell_b.top + cell_b.height || cell_a.top + cell_a.height < cell_b.top);
  },
  randomColor: function () {
    var golden_ratio_conjugate, i, rgb;
    golden_ratio_conjugate = 0.618033988749895;
    if (this.random_color_hue == null) {
      this.random_color_hue = Math.random();
    }
    this.random_color_hue += golden_ratio_conjugate;
    this.random_color_hue %= 1;
    rgb = this.hsvToRgb(this.random_color_hue, this.RANDOM_COLOR_SATURATION, this.RANDOM_COLOR_VALUE);
    return '#' + function () {
      var j, results;
      results = [];
      for (i = j = 0; j <= 2; i = ++j) {
        results.push(('0' + rgb[i].toString(16)).slice(-2));
      }
      return results;
    }().join('');
  },
  shiftColor: function (color, shift) {
    var c, i, j, rgb;
    rgb = color.slice(0, 3);
    for (i = j = 1; j <= 2; i = ++j) {
      c = parseInt(color.substr(i * 2 + 1, 2), 16);
      c = Math.round(Math.min(Math.max(0, c + Math.random() * shift), 255)).toString(16);
      rgb += c.length === 1 ? '0' + c : c;
    }
    return rgb;
  },
  timeTick: function () {
    if (!this.get('reply.solved')) {
      this.set('reply.time_seconds', Math.floor((new Date() - this.get('start_time')) / 1000));
      return Em.run.later(this, this.timeTick, 1000);
    }
  }
});
