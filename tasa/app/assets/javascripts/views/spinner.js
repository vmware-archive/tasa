(function() {
  'use strict';
  window.SpinnerView = Backbone.View.extend({
    initialize: function(options) {
      _.extend(this, _.omit(options, 'model', 'el', '$el'));

      this.listenTo(this.model, 'request', _.partial(this.render, {loading: true}));
      this.listenTo(this.model, 'sync', _.partial(this.render, {loading: false}));
    },

    render: function(options) {
      this.$el.empty();
      var template = options.loading ? 'templates/spinner' : _.result(this, 'template');
      if (template) { this.$el.html(JST[template](this.decorator())); }
      return this;
    },

    decorator: function() {
      return _.result(this.model, 'toJSON');
    }
  });
})();