function editSimpleChoiceQuiz(target, template, source) {
  // `source` will be null if it is a new quiz.
  source = source || {options: []};
  // render Handlebars template and insert it into target
  target.html(template(source));

  // add ability to add options.
  target.find('.add-option').click(function () {
    var row = $('<div class="choice-option"><input type="checkbox" class="is_correct"/><input type="text" class="text"/><span class="remove"></span></div>');
    target.find('.choice-options').append(row);
  });

  target.on('click', '.remove', function() {
    $(this).parent().remove()
  })

  // return and object with a `submit` method.
  // `submit` returns a source, conforming to SimpleChoiceQuiz.Schemas.source
  return {
    'submit': function () {
      var options = target.find('.choice-option').map(function () {
        var t = $(this);
        return {
          'is_correct': t.find('.is_correct').prop('checked'),
          'text': t.find('.text').val()
        };
      }).get();
      return {'options': options };
    }
  };
}
