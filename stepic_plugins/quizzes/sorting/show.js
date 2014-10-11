function showSortingQuiz(target, template, dataset, reply, disabled, quiz_info, status) {
  var new_dataset = _.clone(dataset)
  if ( reply && (status == "correct" || status == "wrong") ) {
    var sorted_options = [], unsorted_options = new_dataset.options;
    for (var i=0; i< reply.ordering.length; i++) {
      sorted_options[i] = unsorted_options[reply.ordering[i]];
    }
    new_dataset.options = sorted_options
  }
  target.html(template(new_dataset));

  if (MathJax) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, target.get()])
  }

  var dragSource = null;
  var options = $(target).find('li');

  options.off()
  if (!status) {
    options.on('dragstart',function(e) {
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
  }
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
