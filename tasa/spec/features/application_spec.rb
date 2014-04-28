require 'spec_helper'

feature 'Application' do
  before do
    visit 'http://localhost:3000/'
  end

  scenario 'Bill searches for "Acrobatics"' do
    expect(page).to have_css('h1')

    page.fill_in(:query, with: 'Acrobatics')
    page.find('.query-input').native.send_keys(:return)

    expect(page).to have_no_css('.ball')
    expect(page).to have_content('Tweets from July 1 - 31 of 2013')

    # actual = page.evaluate_script <<-JS
    #   _.map(d3.select('.total-tweets .graph path').data()[0], function(point) {
    #     return {posted_date: Number(point.posted_date), y: point.y};
    #   });
    # JS
    # expected = [
    #   {posted_date: 1372575600000 - 25200000, y: 14},
    #   {posted_date: 1372662000000 - 25200000, y: 10},
    #   {posted_date: 1372834800000 - 25200000, y: 7},
    #   {posted_date: 1372921200000 - 25200000, y: 8},
    #   {posted_date: 1373007600000 - 25200000, y: 6},
    #   {posted_date: 1373094000000 - 25200000, y: 5},
    #   {posted_date: 1373180400000 - 25200000, y: 5},
    #   {posted_date: 1373266800000 - 25200000, y: 15},
    #   {posted_date: 1373353200000 - 25200000, y: 3},
    #   {posted_date: 1373439600000 - 25200000, y: 9},
    #   {posted_date: 1373612400000 - 25200000, y: 8},
    #   {posted_date: 1373698800000 - 25200000, y: 10},
    #   {posted_date: 1373785200000 - 25200000, y: 11},
    #   {posted_date: 1373871600000 - 25200000, y: 14},
    #   {posted_date: 1373958000000 - 25200000, y: 11},
    #   {posted_date: 1374044400000 - 25200000, y: 9},
    #   {posted_date: 1374130800000 - 25200000, y: 8},
    #   {posted_date: 1374217200000 - 25200000, y: 6},
    #   {posted_date: 1374303600000 - 25200000, y: 9},
    #   {posted_date: 1374390000000 - 25200000, y: 12},
    #   {posted_date: 1374476400000 - 25200000, y: 16},
    #   {posted_date: 1374562800000 - 25200000, y: 5},
    #   {posted_date: 1374649200000 - 25200000, y: 5},
    #   {posted_date: 1374735600000 - 25200000, y: 13},
    #   {posted_date: 1374822000000 - 25200000, y: 5},
    #   {posted_date: 1374908400000 - 25200000, y: 13},
    #   {posted_date: 1374994800000 - 25200000, y: 5},
    #   {posted_date: 1375081200000 - 25200000, y: 17},
    #   {posted_date: 1375167600000 - 25200000, y: 7},
    #   {posted_date: 1375254000000 - 25200000, y: 13}
    # ].map(&:with_indifferent_access)
    # expect(actual).to eq(expected)
    #
    # actual = page.evaluate_script <<-JS
    #   (function() {
    #     var positive = d3.select('.sentiment .graph path[stroke="#d9e021"]').data()[0];
    #     var neutral = d3.select('.sentiment .graph path[stroke="rgba(255, 255, 255, 0.3)"]').data()[0];
    #     var negative = d3.select('.sentiment .graph path[stroke="#e74d00"]').data()[0];
    #
    #     return _.map(positive, function(_, i) {
    #       return {
    #         posted_date: Number(positive[i].posted_date) / 1000,
    #         positive_count: positive[i].y,
    #         neutral_count: neutral[i].y,
    #         negative_count: negative[i].y
    #       };
    #     });
    #   })();
    # JS
    # expected = [
    #   {posted_date: '2013-06-30', neutral_count: 1, negative_count: 3, positive_count: 1},
    #   {posted_date: '2013-07-01', neutral_count: 2, negative_count: 2, positive_count: 0},
    #   {posted_date: '2013-07-03', neutral_count: 1, negative_count: 0, positive_count: 2},
    #   {posted_date: '2013-07-04', neutral_count: 0, negative_count: 1, positive_count: 1},
    #   {posted_date: '2013-07-05', neutral_count: 0, negative_count: 1, positive_count: 0},
    #   {posted_date: '2013-07-06', neutral_count: 0, negative_count: 0, positive_count: 3},
    #   {posted_date: '2013-07-07', neutral_count: 0, negative_count: 1, positive_count: 0},
    #   {posted_date: '2013-07-08', neutral_count: 0, negative_count: 1, positive_count: 3},
    #   {posted_date: '2013-07-09', neutral_count: 0, negative_count: 0, positive_count: 1},
    #   {posted_date: '2013-07-10', neutral_count: 1, negative_count: 0, positive_count: 1},
    #   {posted_date: '2013-07-12', neutral_count: 0, negative_count: 1, positive_count: 0},
    #   {posted_date: '2013-07-13', neutral_count: 0, negative_count: 1, positive_count: 3},
    #   {posted_date: '2013-07-14', neutral_count: 0, negative_count: 3, positive_count: 2},
    #   {posted_date: '2013-07-15', neutral_count: 0, negative_count: 3, positive_count: 4},
    #   {posted_date: '2013-07-16', neutral_count: 0, negative_count: 1, positive_count: 1},
    #   {posted_date: '2013-07-17', neutral_count: 0, negative_count: 1, positive_count: 2},
    #   {posted_date: '2013-07-18', neutral_count: 1, negative_count: 1, positive_count: 2},
    #   {posted_date: '2013-07-19', neutral_count: 0, negative_count: 0, positive_count: 2},
    #   {posted_date: '2013-07-20', neutral_count: 0, negative_count: 1, positive_count: 2},
    #   {posted_date: '2013-07-21', neutral_count: 0, negative_count: 1, positive_count: 2},
    #   {posted_date: '2013-07-22', neutral_count: 0, negative_count: 1, positive_count: 2},
    #   {posted_date: '2013-07-23', neutral_count: 0, negative_count: 0, positive_count: 2},
    #   {posted_date: '2013-07-24', neutral_count: 0, negative_count: 0, positive_count: 3},
    #   {posted_date: '2013-07-25', neutral_count: 0, negative_count: 1, positive_count: 5},
    #   {posted_date: '2013-07-26', neutral_count: 1, negative_count: 2, positive_count: 0},
    #   {posted_date: '2013-07-27', neutral_count: 0, negative_count: 1, positive_count: 3},
    #   {posted_date: '2013-07-28', neutral_count: 0, negative_count: 1, positive_count: 1},
    #   {posted_date: '2013-07-29', neutral_count: 1, negative_count: 1, positive_count: 3},
    #   {posted_date: '2013-07-30', neutral_count: 0, negative_count: 1, positive_count: 0},
    #   {posted_date: '2013-07-31', neutral_count: 1, negative_count: 0, positive_count: 4}
    # ].map!(&:with_indifferent_access).each {|point| point[:posted_date] = Time.zone.parse(point[:posted_date]).to_i }
    # expect(actual).to eq(expected)
    #
    # actual = page.evaluate_script <<-JS
    #   (function() {
    #     var data = d3.selectAll('.graph-rect').data()
    #         startDate = data[0].t;
    #     return data.map(function(point) {
    #       var hours = (point.t - startDate) / (1000 * 60 * 60),
    #           day = Math.floor(hours / 24),
    #           hour = hours - day * 24;
    #       return point.v && {num_tweets: point.v, day: day, hour: hour};
    #     }).filter(Boolean);
    #   })();
    # JS
    # expected = [
    #   {hour: 1, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 3, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 4, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 10, positive: 0, negative: 2, neutral: 0, num_tweets: 2, day: 0},
    #   {hour: 13, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 14, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 15, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 16, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 17, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 0},
    #   {hour: 18, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 0},
    #   {hour: 20, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 22, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 0},
    #   {hour: 23, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 0},
    #   {hour: 0, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 1},
    #   {hour: 1, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 1},
    #   {hour: 2, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 1},
    #   {hour: 4, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 1},
    #   {hour: 7, positive: 1, negative: 2, neutral: 0, num_tweets: 3, day: 1},
    #   {hour: 8, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 1},
    #   {hour: 10, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 1},
    #   {hour: 12, positive: 2, negative: 1, neutral: 0, num_tweets: 3, day: 1},
    #   {hour: 13, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 1},
    #   {hour: 14, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 1},
    #   {hour: 16, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 1},
    #   {hour: 17, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 1},
    #   {hour: 18, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 1},
    #   {hour: 19, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 1},
    #   {hour: 23, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 1},
    #   {hour: 1, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 2},
    #   {hour: 5, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 2},
    #   {hour: 6, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 2},
    #   {hour: 16, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 2},
    #   {hour: 18, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 2},
    #   {hour: 0, positive: 1, negative: 0, neutral: 1, num_tweets: 2, day: 3},
    #   {hour: 6, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 3},
    #   {hour: 7, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 3},
    #   {hour: 8, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 3},
    #   {hour: 9, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 3},
    #   {hour: 12, positive: 3, negative: 0, neutral: 0, num_tweets: 3, day: 3},
    #   {hour: 13, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 3},
    #   {hour: 16, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 3},
    #   {hour: 17, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 3},
    #   {hour: 21, positive: 1, negative: 0, neutral: 1, num_tweets: 2, day: 3},
    #   {hour: 23, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 3},
    #   {hour: 0, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 1, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 4, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 6, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 8, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 9, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 10, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 4},
    #   {hour: 12, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 4},
    #   {hour: 18, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 4},
    #   {hour: 22, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 4},
    #   {hour: 8, positive: 0, negative: 0, neutral: 1, num_tweets: 1, day: 5},
    #   {hour: 12, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 5},
    #   {hour: 14, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 5},
    #   {hour: 15, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 5},
    #   {hour: 17, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 5},
    #   {hour: 18, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 5},
    #   {hour: 2, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 4, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 5, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 6},
    #   {hour: 7, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 11, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 12, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 17, positive: 2, negative: 0, neutral: 0, num_tweets: 2, day: 6},
    #   {hour: 18, positive: 1, negative: 1, neutral: 0, num_tweets: 2, day: 6},
    #   {hour: 19, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 20, positive: 1, negative: 0, neutral: 0, num_tweets: 1, day: 6},
    #   {hour: 23, positive: 0, negative: 1, neutral: 0, num_tweets: 1, day: 6}
    # ].map(&:with_indifferent_access).map {|point| point.except(:positive, :negative, :neutral)}
    # expect(actual).to eq(expected)

    actual = page.all('.drilldown ol li').map do |node|
      {username: node.find('.username').text, text: node.find('.text').text}
    end
    expected = [
      {username: "say4life", text: "acolyte acrobat"},
      {username: "_blasianBOMB", text: "Flip it, acrobat."},
      {username: "KENSHI0504", text: "I like acrobat!!!"},
      {username: "Ash_UpsideDown", text: "Acrobatic makeup sex. 😂"},
      {username: "hunter_kingg", text: "Tobacco packin acrobat"},
      {username: "redbeanns", text: "@YayaRosman acrobatic water skiing!"},
      {username: "MubasherJ7", text: "That was a great acrobatic clearance"},
      {username: "madiharris514", text: "Future career: acrobats :) @H2_hannah9"},
      {username: "DuncanDoeNuts_", text: "Tobacco packing acrobat"},
      {username: "DjScratchez", text: "Flippen the work like an acrobat"},
      {username: "JustJame5", text: "Faculty, office working, acrobats"},
      {username: "KENSHI0504", text: "I like acrobat!!!"},
      {username: "specialistSHY", text: "@ned_cleo heeeoooool... acrobatic moves..."},
      {username: "HappyLikeSiao", text: "acrobatic diving > Junho!!!!!!! ♥♥"},
      {username: "chaisebanks", text: "@SpaceKid_K with that acrobatic cheese lol"},
      {username: "Kitkatkaye", text: "Acrobatic morning y'all! :-D"},
      {username: "CeliaO2", text: "Acrobat reader http://t.co/5zQUCsqXlO"},
      {username: "la1nenu", text: "Acrobatics at night http://t.co/E8u7q6ZYEg"},
      {username: "KutThroatDro", text: "Acrobat shit too many flips"},
      {username: "connor_blackmon", text: "RT @_cwade: Connors an acrobat wtf"}
    ]
    expect(actual - expected).to have_at_most(3).items
    expect(expected - actual).to have_at_most(3).items
    page.find('.drilldown').should have_content('279 Total Tweets')

    actual = page.all('.adjectives .tag-cloud text').map(&:text)
    expected = %w[acrobatic professional good full first free aerial great amazing]
    expect(actual).to include(*expected)

    actual = page.evaluate_script("d3.selectAll('.node').data().length")
    expect(actual).to eq(203)

    page.find('.total-tweets .graph svg > path').hover
    details = page.find('.total-tweets .graph .detail .item')
    details.click
    expect(page.find('.drilldown')).to have_content(details.find('.date').text)
    # expect(page.find('.drilldown')).to have_content(details.find('.tweets').text + ' Total Tweets')

    page.all('.topic-cluster .tag-cloud text', text: 'like').first.click
    expect(page.all('.drilldown .sidebar-tweet .text', text: 'like')).to_not be_empty
  end
end