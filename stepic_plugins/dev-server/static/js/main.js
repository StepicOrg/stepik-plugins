var current_dataset = null;
var shown_quiz = null;
var edited_quiz = null;

function postQuiz() {
  var data = JSON.stringify(edited_quiz.submit());
  $("#show-update-request").text(data);

  $.ajax('quiz/', {
    'type': 'post',
    'data': data,
    'contentType': 'application/json'
  }).done(function (data) {
    $("#show-update-response")
        .text(JSON.stringify(data));
  }).fail(function (data) {
    $("#show-update-response")
        .text("=(\n" + data.responseText);
  });
}

function postSubmission() {
  var data = JSON.stringify(shown_quiz.submit());
  $("#show-submit-request").text(data);

  $.ajax('quiz/submission/', {
    'type': 'post',
    'data': data,
    'contentType': 'application/json'
  }).done(function (data) {
    $("#show-submit-response")
        .text(JSON.stringify(data));
  }).fail(function (data) {
    $("#show-submit-response").text("=(\n" + data.responseText);
  });
}

function getDataset() {
  $.ajax('quiz/attempt/', {
    'type': 'post'
  }).done(function (data) {
    current_dataset = data;
    $("#show-submit-request").text(JSON.stringify(data));
    updateShowInterface(null, false);
  }).fail(function (data) {
    $("#show-submit-response").text("=(\n" + data.responseText);
  });
}


function disableQuiz() {
  var reply = shown_quiz.submit();
  updateShowInterface(reply, true);

}

function updateShowInterface(reply, disabled){
    var target = $("#show-quiz");
    target.empty();

    shown_quiz = Quiz.show_fn(target, Quiz.show_template, current_dataset, reply, disabled, null);
}

function updateEditInterface(data) {
  var target = $('#edit-quiz');
  target.empty();
  edited_quiz = Quiz.edit_fn(target, Quiz.edit_template, data);
}

Quiz = {};

function loadTemplate(name) {
  return $.get('quiz/static/' + name + '.hbs').then(function(src) {
    Quiz[name + '_template'] =  Handlebars.compile(src);
  });
}

function loadFunction(name) {
  $.getScript('quiz/static/'+name+'.js').then(function(src) {
    Quiz[name + '_fn'] = window[name + QUIZ_NAME_CAMELIZED + 'Quiz']
  })
}

$(function(){
  $.when(
    loadFunction('show'),
    loadFunction('edit'),
    loadTemplate('show'),
    loadTemplate('edit')
  ).then(function(){
    $('#update-quiz').click(postQuiz);
    $('#get-dataset').click(getDataset);
    $('#submit-quiz').click(postSubmission);
    $('#disable-quiz').click(disableQuiz);
    updateEditInterface(null);
  }, function(err){
    alert(err.responseText)
  });
});
