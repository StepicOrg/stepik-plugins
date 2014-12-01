function editMatchingQuiz(target, template, source) {
  source = source || {preserve_firsts_order: true, pairs: [{first: 'First', second: 'Second'}]}
  target.html(template(source));
  target.find('.add-pair').click(function () {
    var row = $('<div class="matching-pair" draggable="true">1: <input type="text" class="first"/> 2: <input type="text" class="second"/><span class="remove"></span></div>');
    target.find('.matching-pairs').append(row);
    target.find(".matching-pair").off();
    makeDraggeble();
  });
 target.on('click', '.remove', function() {
   $(this).parent().remove();
   target.find(".matching-pair").off();
   makeDraggeble();
  })



  function makeDraggeble() {
    var dragSource = null;
    var pairs = $(target).find('.matching-pair');

    pairs.off()
    .on('dragstart',function(e) {
      dragSource = this;
      e.originalEvent.dataTransfer.setData('text/html', this.outerHTML);
    })
    .on('dragover',function(e) {
      e.preventDefault();
    })
    .on('drop', function(e) {
      if(pairs.index(dragSource) > pairs.index(this))
        $(this).before(dragSource);
      else
        $(this).after(dragSource);
      pairs = $(target).find('.matching-pair');
    });
  }

  makeDraggeble();

  return {
    'submit': function () {
      var pairs = target.find('.matching-pair').map(function () {
        var t = $(this);
        return {
          'first': t.find('.first').val(),
          'second': t.find('.second').val()
        }
      }).get();
      return {
        'preserve_firsts_order': target.find('.preserve_firsts_order').prop('checked'),
        'pairs': pairs
      };
    }
  };
}


