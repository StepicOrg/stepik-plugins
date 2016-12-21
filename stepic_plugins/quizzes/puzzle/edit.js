var l;
export default Em.Component.extend({
  //
  // Oneliner properties
  //
  max_size: 10 * 1024 * 1024,
  //
  // Event handlers
  //
  setInitial: function () {
    var default_source;
    default_source = {
      image_src: '',
      level: 3
    };
    this.set('source', this.get('source') || default_source);
    return this.sendAction('sourceUpdated', this.get('source'));
  }.on('init'),
  //
  // Methods
  //
  attachFile: function () {
    var file, reader;
    file = this.$('input[type="file"]')[0].files[0];
    if (!file) {
      return;
    }
    if (this.get('max_size') && file.size > this.get('max_size')) {
      this.woof.warning('Max file size to upload: ' + Math.floor(this.get('max_size') / 1024 / 1024) + ' MB.');
      return;
    }
    reader = new FileReader();
    reader.onload = () => {
      return this.set('source.image_src', reader.result);
    };
    return reader.readAsDataURL(file.slice());
  },
  //
  // Actions
  //
  actions: {
    startUpload: function () {
      return this.attachFile();
    }
  },
  //
  // Other
  //
  level_options: function () {
    var i, results;
    results = [];
    for (l = i = 0; i <= 6; l = ++i) {
      results.push({
        value: l,
        label: l + 1
      });
    }
    return results;
  }()
});
