task :compile => :environment do
  Rake::Task['assets:clobber'].invoke
  Rake::Task['assets:precompile'].invoke

  target_dir = Rails.root.join('../webserver/common/static/tasa')
  FileUtils.rm_r target_dir
  FileUtils.cp_r Rails.root.join('public'), target_dir
  FileUtils.cp Dir.glob(Rails.root.join('public/assets/index-*.html')).first, File.join(target_dir, 'index.html')

  Rake::Task['assets:clobber'].execute
end