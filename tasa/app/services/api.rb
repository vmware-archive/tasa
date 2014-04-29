require 'open-uri'
module API
  CACHE = {}
  def self.get(url)
    proxy_url = url.gsub(/:\d+/, ':8081')
    (CACHE[proxy_url] ||= open(proxy_url).read)
  end
end