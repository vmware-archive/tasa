require 'spec_helper'

feature 'Application' do
  before do
    visit '/'
  end

  scenario 'Bill searches for pokemon' do
    expect(page).to have_css('h1')
  end
end