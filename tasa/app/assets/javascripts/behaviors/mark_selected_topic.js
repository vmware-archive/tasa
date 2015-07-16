(function() {
  'use strict';
  window.MarkSelectedTopicBehavior = function(options) {
    var $el = options.el;

    $el
      .on('click', '[data-topic]', function(e) {
        $('.topic-cluster')[0].dataset.selected = $(e.currentTarget).data('topic');
        e.stopPropagation();
      })
      .on('click', '.topic-cluster', function() {
        delete $('.topic-cluster')[0].dataset.selected;
      });
  }
})();