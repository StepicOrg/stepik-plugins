function editSortingQuiz(target, template, source) {
  source = source || {options: []}
  target.html(template(source));
  target.find('.sorting_quiz__add_button').click(function () {
    var row = $('<div class="option"><input type="text" class="text"/></div>');
    target.find('.options').append(row);
  });

  target.find('.sorting_quiz__clear_button').click(function () {
    target.find('.options').empty();
  });

  return {
    'submit': function () {
      var options = target.find('.option').map(function () {
        var t = $(this);
        return t.find('.text').val();
      }).get();
      return {'options': options };
    }
  };
}
