export default Em.Component.extend({
  //
  // Primitive properties (arrays, objects, strings...)
  //
  template_mapping: {
    '#': 'normal',
    '-': 'subsup',
    _: 'sub',
    '^': 'sup'
  },
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      expression: '2H2 + O2 -> 2H2O',
      template: [
        'normal',
        'normal',
        'sub',
        'normal',
        'normal',
        'normal',
        'normal',
        'normal',
        'normal',
        'sub',
        'normal'
      ]
    };
    this.set('source', this.get('source') || default_source);
    this.sendAction('sourceUpdated', this.get('source'));
    return this.set('template_expr', _.map(this.get('source.template'), s => {
      return _.invert(this.get('template_mapping'))[s];
    }).join(''));
  }.on('init'),
  //
  // Observer function
  //
  parseTemplate: function () {
    var template_chars;
    template_chars = _.filter(this.get('template_expr').split(''), c => {
      return c in this.get('template_mapping');
    });
    return this.set('source.template', _.map(template_chars, c => {
      return this.get('template_mapping')[c];
    }));
  }.observes('template_expr')
});
