function showSortingQuiz(target, template, dataset, reply, disabled, quiz_info) {
  if (reply) {
    dataset.options = _(reply.ordering).map(function(i) {
      return dataset.options[i];
    });
  }
  target.html(template(dataset));
  if (MathJax) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, target.get()])
  }

  var dragSource = null;
  var options = $(target).find('li');

  options.off()
  .on('dragstart',function(e) {
    dragSource = this;
    e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
  })
  .on('dragover',function(e) {
    e.preventDefault();
  })
  .on('drop', function(e) {
    if(options.index(dragSource) > options.index(this))
      $(this).before(dragSource);
    else
      $(this).after(dragSource);
    options = $(target).find('li');
  });

  return {
    'submit': function() {
      var ordering = target.find('.sorting-quiz__item_number')
        .map(function () {
          return parseInt($(this).text(), 10);
        }).get();
      return {'ordering': ordering };
    }
  };
}
