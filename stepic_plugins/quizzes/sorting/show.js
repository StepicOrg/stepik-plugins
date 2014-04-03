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
  target.find("li").on('dragstart',function () {
    dragSource = this;
  }).on('dragover',function (e) {
    e.preventDefault();
  }).on('drop', function () {
    var tmp = dragSource.innerHTML;
    dragSource.innerHTML = this.innerHTML;
    this.innerHTML = tmp;
  });

  return {
    'submit': function () {
      var ordering = target.find('.sorting-quiz__item_number')
        .map(function () {
          return parseInt($(this).text(), 10);
        }).get();
      return {'ordering': ordering };
    }
  };
}
