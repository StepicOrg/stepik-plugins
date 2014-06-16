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
  target.find("li").on('dragstart',function (e) {
    dragSource = this;
    e.originalEvent.dataTransfer.setData('text/html', $(this).html())
    $(dragSource).addClass('dragged');
  }).on('dragover',function (e) {
    e.preventDefault();
  }).on('drop', function () {
    var tmp = dragSource.innerHTML;
    dragSource.innerHTML = this.innerHTML;
    this.innerHTML = tmp;
    $(dragSource).removeClass('dragged')
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
