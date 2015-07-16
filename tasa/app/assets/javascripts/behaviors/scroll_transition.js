(function() {
  'use strict';
  window.ScrollTransitionBehavior = function(options) {
    var $el = options.el;

    $el.one('webkitTransitionEnd', function() {
      var
        queryNode =  $el.find('.query'),
        queryThreshold = queryNode.offset().top,
        drilldownThreshold = $el.find('.drilldown').offset().top,
        contentTop = $el.find('.graphs').offset().top,
        start = queryThreshold + 130,
        finish = contentTop - queryNode.outerHeight() + 30
        ;

      $(window).scroll(function() {
        var
          scrollTop = $el.scrollTop(),
          opacity = Math.min(Math.max((scrollTop - start) / (finish - start), 0), 0.99)
        ;
        queryNode.toggleClass('sticky',  scrollTop > queryThreshold);
        $el.find('.drilldown').toggleClass('sticky',  scrollTop > drilldownThreshold);

        queryNode.css('background-color', queryNode.css('background-color').replace(/[\d.]+(?=\))/, opacity));
      });
    });
  };
})();