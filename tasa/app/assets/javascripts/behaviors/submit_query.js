(function() {
  'use strict';
  var DEFAULT_TOPICS = 3;

  window.SubmitQueryBehavior = function(options) {
    var $el = options.el,
        model = options.model,
        resources = options.resources;

    $el.on('submit', 'form', function(e) {
      var $form = $(e.currentTarget);

      _.each($form.serializeArray(), function(input) {
        if (input.name === 'query') {
          var parsedQuery = input.value.split(/\s*\|\s*/);
          model.set({query: parsedQuery[0], topics: parsedQuery[1] || DEFAULT_TOPICS});
        } else if (input.name === 'topics') {
          model.set(input.name, Number(input.value))
        }

        $form.find('[name="' + input.name + '"]').val(model.get(input.name));
      });
      $(document.activeElement).blur();
    });

    var xhrRequests, forceXhrRequest;
    model.on('change', function() {
      var oldXhrRequests = xhrRequests;
      xhrRequests = [];

      resources.drilldown.clear({silent: true});

      if (_.has(model.changedAttributes(), 'query')) {
        _.invoke(oldXhrRequests, 'abort');
        _.result(forceXhrRequest, 'abort');

        $('body').toggleClass('has-query', Boolean(model.get('query')));
        xhrRequests = _.invoke(_.values(resources), 'fetch', {reset: true, silent: true});
        forceXhrRequest = resources.force.fetch({reset: true, silent: true});
      } else if (_.has(model.changedAttributes(), 'topics')) {
        _.result(forceXhrRequest, 'abort');
        forceXhrRequest = resources.force.fetch({reset: true, silent: true});
      }
    });
  }
})();