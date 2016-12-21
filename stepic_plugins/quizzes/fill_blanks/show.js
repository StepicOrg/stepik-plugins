export default Em.Component.extend({
  //
  // Event handlers
  //
  setInitial: function () {
    var blank_index, c, component, components, i, len, ref;
    if (this.get('reply') == null) {
      this.set('reply', {
        blanks: function () {
          var i, len, ref, results;
          ref = this.get('dataset.components');
          results = [];
          for (i = 0, len = ref.length; i < len; i++) {
            c = ref[i];
            if (c.type !== 'text') {
              results.push('');
            }
          }
          return results;
        }.call(this)
      });
      this.sendAction('replyUpdated', this.get('reply'));
    }
    components = [];
    blank_index = 0;
    ref = this.get('dataset.components');
    for (i = 0, len = ref.length; i < len; i++) {
      component = ref[i];
      components.push({
        type: component.type,
        text: component.type === 'text' ? component.text : this.get('reply.blanks.' + blank_index),
        options: component.type === 'select' ? [''].concat(component.options) : []
      });
      if (component.type !== 'text') {
        blank_index += 1;
      }
    }
    return this.set('components', components);
  }.on('init'),
  //
  // Observer function
  //
  onBlankChanged: function () {
    var c;
    this.set('reply', {
      blanks: function () {
        var i, len, ref, results;
        ref = this.get('components');
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          c = ref[i];
          if (c.type !== 'text') {
            results.push(c.text);
          }
        }
        return results;
      }.call(this)
    });
    return this.sendAction('replyUpdated', this.get('reply'));
  }.observes('components.@each.text')
});
