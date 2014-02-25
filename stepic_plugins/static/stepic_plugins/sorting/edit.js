function editSortingQuiz(target, template, source) {
  target.html(template(source));
  target.find('button').click(function () {
    var row = $('<div class="option"><input type="text" class="text"/></div>');
    target.find('.options').append(row);
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
