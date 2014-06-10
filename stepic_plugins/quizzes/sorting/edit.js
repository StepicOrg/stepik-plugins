function editSortingQuiz(target, template, source) {
  source = source || {options: []}
  target.html(template(source));
  target.find('.add-option').click(function () {
    var row = $('<div class="sort-option"><input type="text" class="text"/><span class="remove"></span></div>');
    target.find('.sort-options').append(row);
  });
 target.on('click', '.remove', function() {
    $(this).parent().remove()
  })

  return {
    'submit': function () {
      var options = target.find('.sort-option').map(function () {
        var t = $(this);
        return t.find('.text').val();
      }).get();
      return {'options': options };
    }
  };
}
