require 'spec_helper'

feature 'Application' do
  before do
    visit '/'
  end

  scenario 'Bill searches for "Acrobatics"' do
    expect(page).to have_css('h1')

    page.fill_in(:query, with: 'Acrobatics')
    page.find('.query-input').native.send_keys(:return)

    expect(page).to have_content('Tweets from July 1 - 31 of 2013')
  end
end