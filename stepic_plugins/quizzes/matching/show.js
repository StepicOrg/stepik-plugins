function showMatchingQuiz(target, template, dataset, reply, disabled, quiz_info) {
  var new_dataset = _.clone(dataset)
  if ( reply ) {
    var sorted_pairs = [], unsorted_pairs = new_dataset.pairs;
    for (var i=0; i< reply.ordering.length; i++) {
      sorted_pairs[i] = unsorted_pairs[reply.ordering[i]];
    }
    new_dataset.pairs = sorted_pairs
  }
  target.html(template(new_dataset));

  /*if (MathJax) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, target.get()])
  }*/

  var dragSource = null;
  var pairs = $(target).find('li');

  pairs.off()
  if (!disabled) {
    pairs.on('dragstart',function(e) {
      dragSource = this;
      e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
    })
    .on('dragover',function(e) {
      e.preventDefault();
    })
    .on('drop', function(e) {
      if(pairs.index(dragSource) > pairs.index(this))
        $(this).before(dragSource);
      else
        $(this).after(dragSource);
      pairs = $(target).find('li');
    });
  }
  return {
    'submit': function() {
      var ordering = target.find('.matching-quiz__second-item_number')
        .map(function () {
          return parseInt($(this).text(), 10);
        }).get();
      return {'ordering': ordering };
    }
  };
}
