function showSimpleChoiceQuiz(target, template, dataset, reply, disabled, quiz_info) {
  var selections = dataset.options.map(function (o) {
    return {"text": o };
  });
  if (reply) {
    reply.choices.forEach(function (o, i) {
      selections[i].is_checked = o;
    });
  }
  var context = {
    'selections': selections,
    'disabled': disabled
  };
  target.html(template(context));
  return {
    'submit': function () {
      var choices = target.find("input").map(function () {
        return $(this).prop("checked");
      }).get();
      return {'choices': choices };
    }
  };
}
