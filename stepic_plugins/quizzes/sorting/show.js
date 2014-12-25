function showSortingQuiz(target, template, dataset, reply, disabled, quiz_info) {
  var new_dataset = _.clone(dataset)
  if ( reply ) {
    var sorted_options = [], unsorted_options = new_dataset.options;
    for (var i=0; i< reply.ordering.length; i++) {
      sorted_options[i] = unsorted_options[reply.ordering[i]];
    }
    new_dataset.options = sorted_options
  }
  target.html(template(new_dataset));

  /*if (MathJax) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, target.get()])
  }*/

  var dragSource = null;
  var options = $(target).find('li');

  options.off()
  if (!disabled) {
    options.on('dragstart',function(e) {
      dragSource = this;
      $(this).addClass('sorting-quiz__item-extracted');
      e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
    })
    .on('dragover',function(e) {
      options.removeClass('sorting-quiz__item-insert-before')
      .removeClass('sorting-quiz__item-insert-after');
      if(options.index(dragSource) > options.index(this))
        $(this).addClass('sorting-quiz__item-insert-before')
      else
        $(this).addClass('sorting-quiz__item-insert-after')
      e.preventDefault();
    })
    .on('dragend', function(e) {
      options.removeClass('sorting-quiz__item-insert-before')
      .removeClass('sorting-quiz__item-insert-after')
      .removeClass('sorting-quiz__item-extracted');
    })
    .on('dragleave', function(e) {
      options.removeClass('sorting-quiz__item-insert-before')
      .removeClass('sorting-quiz__item-insert-after');
    })
    .on('drop', function(e) {
      if(options.index(dragSource) > options.index(this))
        $(this).before(dragSource);
      else
        $(this).after(dragSource);
      options = $(target).find('li');
    });
    $(target).find('.sorting-quiz__arrow-up').off()
    .on('click', function(e){
      $(this.parentElement.previousElementSibling).before(this.parentElement);
      options = $(target).find('li');
    });
    $(target).find('.sorting-quiz__arrow-down').off()
    .on('click', function(e){
      $(this.parentElement.nextElementSibling).after(this.parentElement);
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
