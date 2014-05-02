(function() {
  'use strict';

  window.DrilldownView = SpinnerView.extend({
    template: 'templates/sidebar_tweets',
    decorator: function(options) {
      if (options.loading) { return {}; }

      return _.extend(this.model.omit('tweets'), {
        date: this.model.has('posted_date') && d3.time.format.utc('%B %d, %Y')(new Date(this.model.get('posted_date'))) ||
          this.model.has('heatmap') && d3.time.format('%As at %I%p')(new Date(this.model.get('heatmap'))).replace(/at 0/, 'at ') ||
          'July 1 - 31, 2013',
        title: this.model.get('sentiment') && 'Sentiment Mapping' ||
          this.model.get('topic') && 'Topic Words' ||
          this.model.get('adjective') && 'Adjectives' ||
          this.model.get('heatmap') && 'Tweet Activity' ||
          'Top ' + this.model.get('tweets').total.length + ' Tweets',
        proportions: (this.model.get('sentiment') || this.model.get('heatmap')) && {
          positive_proportion: 100 * this.model.get('counts').positive / this.model.get('counts').total,
          negative_proportion: 100 * this.model.get('counts').negative / this.model.get('counts').total,
          neutral_proportion: 100 * this.model.get('counts').neutral / this.model.get('counts').total
        } || undefined,
        breakdown: this.model.get('sentiment') || this.model.get('heatmap'),
        groups: _.map(this.model.get('tweets'), function(tweets, sentiment) {
          if (this.model.get('sentiment') && this.model.get('sentiment') !== sentiment) { return; }

          return {
            sentiment: sentiment,
            tweets: tweets,
            subtitle: (this.model.get('sentiment') || this.model.get('heatmap')) && 'Top ' + tweets.length + ' ' + sentiment + ' tweets' ||
              this.model.get('adjective') && 'Top ' + tweets.length + ' tweets for "' + this.model.get('adjective') + '"' ||
              ''
          }
        }, this)
      });
    },
    render: function() {
      SpinnerView.prototype.render.apply(this, arguments);
      this.$el.parent().scrollTop(0);
    }
  });
})();