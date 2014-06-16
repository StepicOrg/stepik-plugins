function editSortingQuiz(target, template, source) {
  source = source || {options: []}
  target.html(template(source));
  target.find('.add-option').click(function () {
    var row = $('<div class="sort-option" draggable="true"><input type="text" class="text"/><span class="remove"></span></div>');
    target.find('.sort-options').append(row);
    target.find(".sort-option").off();
    makeDraggeble();
  });
 target.on('click', '.remove', function() {
    $(this).parent().remove()
  })

  var dragSource = null;

  function makeDraggeble() {
    target.find(".sort-option").on('dragstart',function (e) {
      dragSource = this;
      e.originalEvent.dataTransfer.setData('text/html', $(this).html())
      $(dragSource).addClass('dragged');
    }).on('dragover',function (e) {
      e.preventDefault();
    }).on('drop', function () {
      var tmp = dragSource.innerHTML;
      dragSource.innerHTML = this.innerHTML;
      this.innerHTML = tmp;
      $(dragSource).removeClass('dragged')
    });
  }

  makeDraggeble();

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


