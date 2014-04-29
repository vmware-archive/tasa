class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  def proxy
    render json: API.get(request.original_url)
  end
end
