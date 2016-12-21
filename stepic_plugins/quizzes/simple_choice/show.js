function showSimpleChoiceQuiz(target, template, dataset, reply, disabled) {
  // prepare context for the template
  var selections = dataset.options.map(function (o) {
    return {
      text: o,
      is_checked: false
    };
  });
  // if reply given, mark selected option
  if (reply) {
    reply.choices.forEach(function (o, i) {
      selections[i].is_checked = o;
    });
  }
  var context = {
    selections: selections,
    disabled: disabled
  };
  // display template
  target.html(template(context));
  // return an object with `submit` method, which returns reply
  // conforming to SimpleChoiceQuiz.Schemas.reply
  return {
    submit: function () {
      var choices = target.find('input').map(function () {
        return $(this).prop('checked');
      }).get();
      return {choices: choices};
    }
  };
}
