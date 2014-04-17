require 'spec_helper'

feature 'Application' do
  before do
    visit 'http://localhost:3000/'
  end

  scenario 'Bill searches for "Acrobatics"' do
    expect(page).to have_css('h1')

    page.fill_in(:query, with: 'Acrobatics')
    page.find('.query-input').native.send_keys(:return)

    expect(page).to have_content('Tweets from June 30 - July 31 of 2013')
    expect(page).to have_css('.rickshaw_graph')

    actual = page.evaluate_script <<-JS
      _.map(d3.select('.total-tweets .graph path').data()[0], function(point) {
        return {posted_date: Number(point.posted_date), y: point.y};
      });
    JS

    expected = [
      {posted_date: 1372575600000 - 25200000, y: 14},
      {posted_date: 1372662000000 - 25200000, y: 10},
      {posted_date: 1372834800000 - 25200000, y: 7},
      {posted_date: 1372921200000 - 25200000, y: 8},
      {posted_date: 1373007600000 - 25200000, y: 6},
      {posted_date: 1373094000000 - 25200000, y: 5},
      {posted_date: 1373180400000 - 25200000, y: 5},
      {posted_date: 1373266800000 - 25200000, y: 15},
      {posted_date: 1373353200000 - 25200000, y: 3},
      {posted_date: 1373439600000 - 25200000, y: 9},
      {posted_date: 1373612400000 - 25200000, y: 8},
      {posted_date: 1373698800000 - 25200000, y: 10},
      {posted_date: 1373785200000 - 25200000, y: 11},
      {posted_date: 1373871600000 - 25200000, y: 14},
      {posted_date: 1373958000000 - 25200000, y: 11},
      {posted_date: 1374044400000 - 25200000, y: 9},
      {posted_date: 1374130800000 - 25200000, y: 8},
      {posted_date: 1374217200000 - 25200000, y: 6},
      {posted_date: 1374303600000 - 25200000, y: 9},
      {posted_date: 1374390000000 - 25200000, y: 12},
      {posted_date: 1374476400000 - 25200000, y: 16},
      {posted_date: 1374562800000 - 25200000, y: 5},
      {posted_date: 1374649200000 - 25200000, y: 5},
      {posted_date: 1374735600000 - 25200000, y: 13},
      {posted_date: 1374822000000 - 25200000, y: 5},
      {posted_date: 1374908400000 - 25200000, y: 13},
      {posted_date: 1374994800000 - 25200000, y: 5},
      {posted_date: 1375081200000 - 25200000, y: 17},
      {posted_date: 1375167600000 - 25200000, y: 7},
      {posted_date: 1375254000000 - 25200000, y: 13}
    ].map(&:with_indifferent_access)

    expect(actual).to eq(expected)
  end
end