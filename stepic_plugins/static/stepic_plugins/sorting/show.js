function showSortingQuiz(target, template, dataset, reply, disabled, quiz_info) {
  target.html(template(dataset));
  var dragSource = null;

  target.find("li").on('dragstart', function(e){
    dragSource = this;
  }).on('dragover', function(e){
    e.preventDefault();
  }).on('drop', function(e){
    var tmp = dragSource.innerHTML;
    dragSource.innerHTML = this.innerHTML;
    this.innerHTML = tmp;
  });

  return {
    'submit': function () {
      ordering = target.find('.sorting-quiz__item_number')
      .map(function() {
        return parseInt($(this).text(), 10);
      }).get();
      return {'ordering': ordering };
    }
  };
}
