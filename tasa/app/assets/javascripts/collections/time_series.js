(function() {
  'use strict';
  
  window.TimeSeries = Backbone.Collection.extend({
    comparator: 'posted_date',
    model: Backbone.Model.extend({
      idAttribute: 'posted_date',
      parse: function(data) { return _.extend(data, {posted_date: new Date(data.posted_date)}); }
    })
  });
})();