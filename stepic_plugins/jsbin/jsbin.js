function editQuiz(target, template, source) {
  return {
    'submit': function () {
      //WRITE YOUR CODE HERE
      return {};
    }
  };
}

function showQuiz(target, template, dataset, reply, disabled, quiz_info) {
  return {
    'submit': function () {
      //WRITE YOUR CODE HERE
      return {};
    }
  };
}

var current_dataset = null;
var shown_quiz = null;
var edited_quiz = null;
var localhost = "http://127.0.0.1:5000/";

function postQuiz() {
  var data = JSON.stringify(edited_quiz.submit());
  $("#show-update-request").text(data);

  $.ajax(localhost, {
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

  $.ajax(localhost + 'submission/', {
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
  $.ajax(localhost + 'attempt/', {
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

function updateShowInterface(reply, disabled) {
  var target = $("#show-quiz");
  target.empty();
  var template = getTemplate('show-template');
  shown_quiz = showQuiz(target, template, current_dataset, reply, disabled, null);
}

function updateEditInterface(data) {
  var target = $('#edit-quiz');
  target.empty();
  var template = getTemplate('edit-template');
  edited_quiz = editQuiz(target, template, data);
}

function getTemplate(name) {
  return Handlebars.compile($('#' + name).html());
}

$('#update-quiz').click(postQuiz);
$('#get-dataset').click(getDataset);
$('#submit-quiz').click(postSubmission);
$('#disable-quiz').click(disableQuiz);

updateEditInterface({});
