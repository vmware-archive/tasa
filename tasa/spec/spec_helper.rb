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
Capybara.default_wait_time = 5

Dir[Rails.root.join('spec/support/**/*.rb')].each { |f| require f }

RSpec.configure do |config|
  module Helpers
    Dir[Rails.root.join('spec/fixtures/*.json')].each do |file|
      define_method(File.basename(file, '.json')) { JSON.parse(File.read(file)) }
    end
  end
  config.include Helpers

  config.order = 'random'

  config.before do
    API.stub(:get) {|url| fixtures[url.gsub(%r{http://.+?/}, '/')] }
  end
end
