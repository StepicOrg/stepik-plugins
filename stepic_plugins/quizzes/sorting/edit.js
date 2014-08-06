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
   $(this).parent().remove();
   target.find(".sort-option").off();
   makeDraggeble();
  })



  function makeDraggeble() {
    var dragSource = null;
    var options = $(target).find('.sort-option');

    options.off()
    .on('dragstart',function(e) {
      dragSource = this;
      e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
    })
    .on('dragover',function(e) {
      e.preventDefault();
    })
    .on('drop', function(e) {
      if(options.index(dragSource) > options.index(this))
        $(this).before(dragSource);
      else
        $(this).after(dragSource);
      options = $(target).find('.sort-option');
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


