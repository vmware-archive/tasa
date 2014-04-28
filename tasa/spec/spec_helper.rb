ENV['RAILS_ENV'] = 'test'
require File.expand_path('../../config/environment', __FILE__)
require 'rspec/rails'

require 'capybara/rails'
require 'capybara/poltergeist'
Capybara.register_driver :selenium do |app|
  Capybara::Selenium::Driver.new(app, browser: :chrome)
end
# Capybara.default_driver = :poltergeist
Capybara.default_driver = :selenium
Capybara.default_wait_time = 60

Dir[Rails.root.join('spec/support/**/*.rb')].each { |f| require f }

RSpec.configure do |config|
  config.order = 'random'
end
