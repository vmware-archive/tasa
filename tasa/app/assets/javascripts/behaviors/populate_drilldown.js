(function() {
  'use strict';

  window.PopulateDrilldownBehavior = function(options) {
    var model = options.model,
        resources = options.resources,
        $el = options.el;

    $el.on('click', '.detail, .tag-cloud text, .graph-rect', function(e) {
      model.set({
        posted_date: $(e.currentTarget).find('[data-posted-date]').data('posted-date'),
        sentiment: $(e.currentTarget).find('[data-sentiment]').data('sentiment'),
        adjective: $(e.currentTarget).data('adjective'),
        topic: $(e.currentTarget).data('topic'),
        heatmap: $(e.currentTarget).data('heatmap-timestamp')
      });
    });

    model.on('change', function() {
      if (model.get('adjective') && model.get('topic')) {
        var ids = _.result(resources.force.get('topic_words')[model.get('adjective')], model.get('topic')) || [];
        model.set(model.parse({
          tweets: {total: _.values(_.pick(resources.force.get('tweets'), ids))},
          counts: {total: ids.length}
        }), {silent: true});
      } else {
        model.set(model.parse(
            model.get('adjective') && resources.adjectives.get(model.get('adjective')).toJSON() ||
            model.get('heatmap') && resources.tweetActivity.get(model.get('heatmap')).toJSON() ||
            model.get('sentiment') && resources.sentimentMapping.get(new Date(model.get('posted_date'))).toJSON() ||
            model.get('posted_date') && resources.totalTweets.get(new Date(model.get('posted_date'))).toJSON()
        ), {silent: true});
      }
      model.trigger('sync');
    });
  }
})();