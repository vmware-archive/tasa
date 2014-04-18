require 'open-uri'
class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  CACHE = {}
  def proxy
    render json: (CACHE[proxy_url] ||= open(proxy_url).read)
  end

  private

  def proxy_url
    request.original_url.gsub(':3000', ':8081')
  end
end
