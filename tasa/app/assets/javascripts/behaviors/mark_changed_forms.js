(function() {
  'use strict';
  window.MarkChangedFormsBehavior = function(options) {
    var $el = options.el;

    function dirtyForm(e) {
      _.defer(function() {
        var $inputs = $(e.currentTarget).find('input');
        $inputs.each(function() {
          var $input = $(this);
          $input.toggleClass('changed', ($input.attr('value') || '') !== ($input.val() || ''));
        });
      });
    }

    $el
      .on('input', 'form', dirtyForm)
      .on('reset', 'form', dirtyForm)
    ;
  }
})();