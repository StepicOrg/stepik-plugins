export default Em.Component.extend({
  //
  // Simple computed properties
  //
  is_puzzle_visible: Em.computed.or('is_puzzle_loaded', 'disabled'),
  //
  // Computed property functions
  //
  is_puzzle_block_rendered: function () {
    return !this.get('disabled') || this.get('reply.solved');
  }.property('disabled', 'reply.solved'),
  //
  // Event handlers
  //
  cutImage: function () {
    var image = $('.puzzle-quiz__image')[0];
    if (this.get('disabled')) {
      return;
    }
    image.onload = () => {
      snapfit.add(image, this.get('snapfit_options'));
      if (!this.get('isDestroying')) {
        this.set('is_puzzle_loaded', true);
      }
      delete snapfit.solve;
    };
  }.on('didInsertElement'),
  setInitial: function () {
    if (this.get('reply') == null) {
      this.set('reply', {solved: false});
      this.sendAction('replyUpdated', this.get('reply'));
    }
    var solve_callback = () => {
      this.set('reply', {solved: true});
      snapfit.remove($('.puzzle-quiz__image')[0]);
      this.sendAction('replyUpdated', this.get('reply'));
    };
    this.set('snapfit_options', {
      level: this.get('dataset.level'),
      space: 35,
      snap: 5,
      mixed: true,
      simple: true,
      nokeys: true,
      polygon: true,
      aborder: true,
      bwide: 1,
      callback: solve_callback
    });
  }.on('init')
});
