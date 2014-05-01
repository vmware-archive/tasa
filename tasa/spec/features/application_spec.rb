require 'spec_helper'

feature 'Application' do
  let(:fixtures) do
    {
      '/gp/tasa/total_tweets/q?sr_trm=pokemon' => total_tweets,
      '/gp/tasa/sentiment_mapping/q?sr_trm=pokemon' => sentiment_mapping,
      '/gp/tasa/tweet_activity/q?sr_trm=pokemon' => tweet_activity,
      '/gp/tasa/adjectives/q?sr_trm=pokemon' => adjectives,

      '/gp/topic/fetch/q?num_topics=3&sr_trm=pokemon' => topic_cluster_for_3_topics,
      '/gp/topic/fetch/q?num_topics=4&sr_trm=pokemon' => topic_cluster_for_4_topics,

      '/gp/tasa/top_tweets/q?sr_trm=pokemon&sr_adj=' => top_20_tweets,
      '/gp/tasa/top_tweets/q?sr_trm=pokemon&sr_adj=new' => top_20_tweets_for_new
    }
  end

  before do
    visit root_path
  end

  def search_for(query)
    page.fill_in(:query, with: query)
    page.find('.query-input').native.send_keys(:return)
  end

  scenario 'Bill searches for "pokemon"' do
    expect(page).to have_css('h1')

    search_for 'pokemon'

    expect(page).to have_no_css('.ball')
    expect(page).to have_content('Tweets from July 1 - 31 of 2013')

    actual = page.all('.drilldown ol li').map do |node|
      {username: node.find('.username').text, text: node.find('.text').text}.with_indifferent_access
    end
    expected = top_20_tweets['tweets']['total'].map {|point| point.slice('username', 'text')}
    expect(actual).to eq(expected)
    page.find('.drilldown').should have_content("#{top_20_tweets['counts']['total']} Total Tweets")

    actual = page.evaluate_script <<-JS
      _.pluck(d3.select('.total-tweets .graph path').data()[0], 'y');
    JS
    expected = total_tweets.sort_by {|point| point['posted_date']}.map {|point| point['counts']['total']}
    expect(actual).to eq(expected)

    actual = page.evaluate_script <<-JS
      (function() {
        var positive = d3.select('.sentiment .graph path.positive').data()[0],
            neutral = d3.select('.sentiment .graph path.neutral').data()[0],
            negative = d3.select('.sentiment .graph path.negative').data()[0];

        return _.map(positive, function(_, i) {
          return {
            positive: positive[i].y,
            neutral: neutral[i].y,
            negative: negative[i].y
          };
        });
      })();
    JS
    expected = sentiment_mapping.sort_by {|point| point['posted_date']}.map {|point| point['counts'].except('total')}
    expect(actual).to eq(expected)

    actual = page.evaluate_script <<-JS
      (function() {
        var data = d3.selectAll('.graph-rect').data()
            startDate = data[0].t;
        return data.map(function(point) {
          var hours = (point.t - startDate) / (1000 * 60 * 60),
              day = Math.floor(hours / 24),
              hour = hours - day * 24;
          return point.v && {num_tweets: point.v, day: day, hour: hour};
        }).filter(Boolean);
      })();
    JS
    expected = tweet_activity.sort_by {|point| [point['day'], point['hour']]}.map {|point| point.slice('day', 'hour').merge('num_tweets' => point['counts']['total'])}
    expect(actual).to eq(expected)

    page.all('.graph-rect').first.click
    expect(page.find('.drilldown-overview')).to have_content("#{expected[0]['num_tweets']} Total Tweets")
    expect(page.find('.drilldown-overview')).to have_content('Mondays at 12AM')
    expect(page.find('.drilldown')).to have_content('@kiaraajw  what is this Pokemon?o.O')

    # actual = page.all('.adjectives .tag-cloud text').map(&:text)
    # expected = adjectives['adjective_cloud'].sort {|point| -point['normalized_frequency']}.take(64).map {|point| point['word']}
    # expect(actual).to eq(expected)

    actual = page.evaluate_script("d3.selectAll('.node').data().length")
    expected = JSON.parse(topic_cluster_for_3_topics['topic_graph'])['nodes'].length
    expect(actual).to eq(expected)

    expect(page.all('.topic-cluster .force-legend .swatch')).to have(3).topics

    page.find('.total-tweets .graph svg > path').hover
    details = page.find('.total-tweets .graph .detail .item')
    details.click
    expect(page.find('.drilldown')).to have_content('July 16, 2013')

    expected = total_tweets.detect {|r| r['posted_date'] == DateTime.parse('July 16, 2013').to_i * 1000}['counts']['total']
    expect(page.find('.drilldown')).to have_content("#{expected} Total Tweets")

    page.all('.topic-cluster .tag-cloud text', text: 'plai').first.click
    expect(page.all('.drilldown .sidebar-tweet .text', text: 'play')).to_not be_empty
  end

  scenario 'Bill searches for "pokemon | 4" and changes the number of topics to 3' do
    search_for 'pokemon | 4'
    expect(page).to have_no_css('.ball')
    expect(page.all('.topic-cluster .force-legend .swatch')).to have(4).topics

    page.fill_in('Number of topics', with: 3)
    page.find('[name="topics"]').native.send_keys(:return)
    expect(page).to have_no_css('.ball')
    expect(page.all('.topic-cluster .force-legend .swatch')).to have(3).topics
  end
end