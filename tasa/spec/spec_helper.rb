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
  config.before(:suite) do
    ActiveRecord::Migration.check_pending! if defined?(ActiveRecord::Migration)
  end

  config.fixture_path = "#{::Rails.root}/spec/fixtures"

  config.use_transactional_fixtures = false
  config.before { DatabaseCleaner.strategy = :transaction }
  config.before(type: feature) { DatabaseCleaner.strategy = :truncation }
  config.before { DatabaseCleaner.start }
  config.after { DatabaseCleaner.clean }

  config.order = 'random'
end
