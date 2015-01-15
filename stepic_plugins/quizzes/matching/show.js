function showMatchingQuiz(target, template, dataset, reply, disabled, quiz_info) {
  var new_dataset = _.clone(dataset);
  if ( reply ) {
    var unsorted_first_values  = new_dataset.pairs.map(function(pair){return pair.first;});
    var unsorted_second_values = new_dataset.pairs.map(function(pair){return pair.second;});
    var sorted_second_values   = reply.ordering.map(function(index){return unsorted_second_values[index];});
    new_dataset.pairs = _.zip(unsorted_first_values, sorted_second_values).map(function(first_second){
      return {first: first_second[0], second: first_second[1]};
    });
  }
  target.html(template(new_dataset));

  /*if (MathJax) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, target.get()])
  }*/

  var dragSource = null;
  var pairs = $(target).find('li');
  pairs.off();
  if (disabled) {
    $(target).find('.matching-quiz__arrow-up').remove();
    $(target).find('.matching-quiz__arrow-down').remove();
    pairs.addClass('matching-quiz__disabled');
    pairs.attr('draggable', false);
  } else {
    pairs.on('dragstart',function(e) {
      dragSource = this;
      $(this).addClass('matching-quiz__item-extracted');
      e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
    })
    .on('dragover',function(e) {
      pairs.removeClass('matching-quiz__item-insert-before')
      .removeClass('matching-quiz__item-insert-after');
      if(pairs.index(dragSource) > pairs.index(this))
        $(this).addClass('matching-quiz__item-insert-before')
      else
        $(this).addClass('matching-quiz__item-insert-after')
      e.preventDefault();
    })
    .on('dragend', function(e) {
      pairs.removeClass('matching-quiz__item-insert-before')
      .removeClass('matching-quiz__item-insert-after')
      .removeClass('matching-quiz__item-extracted');
    })
    .on('dragleave', function(e) {
      pairs.removeClass('matching-quiz__item-insert-before')
      .removeClass('matching-quiz__item-insert-after');
    })
    .on('drop', function(e) {
      if(pairs.index(dragSource) > pairs.index(this))
        $(this).before(dragSource);
      else
        $(this).after(dragSource);
      pairs = $(target).find('li');
    });
    $(target).find('.matching-quiz__arrow-up').off()
    .on('click', function(e){
      $(this.parentElement.previousElementSibling).before(this.parentElement);
      pairs = $(target).find('li');
    });
    $(target).find('.matching-quiz__arrow-down').off()
    .on('click', function(e){
      $(this.parentElement.nextElementSibling).after(this.parentElement);
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
