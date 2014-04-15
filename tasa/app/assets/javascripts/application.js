//= require jquery
//= require jquery_ujs
//= require lodash
//= require handlebars.runtime
//= require backbone
//= require templates/application
(function() {
  'use strict';
   var query = window.query = new Backbone.Model({query: ''});

  $('body').html(JST['templates/application']);

  $('body').on('submit', '.query', function(e) {
    _.each($(e.currentTarget).serializeArray(), function(input) {
      query.set(input.name, input.value);
    });
    $(document.activeElement).blur();
  });

  query.on('change:query', function(query, value) {
    $('body').toggleClass('has-query', Boolean(value));
  });
})();