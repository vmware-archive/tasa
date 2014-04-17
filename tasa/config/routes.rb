Rails.application.routes.draw do
  mount JasmineRails::Engine => '/specs' if defined?(JasmineRails)
  root to: 'application#index'
  get '*path', to: 'application#proxy'
end
