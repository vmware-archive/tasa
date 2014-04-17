require 'open-uri'
class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  def proxy
    render json: open(request.original_url.gsub(':3000', ':8081')).read
  end
end
