#!/usr/bin/env ruby
require 'fileutils'
require 'tmpdir'

# The fixture site uses Jekyll itself, without loading production plugins/data.
ENV['JEKYLL_NO_BUNDLER_REQUIRE'] = 'true'
require 'jekyll'

abort 'Usage: ruby tools/build_snapshot_fixtures.rb DESTINATION' unless ARGV.length == 1
root = File.expand_path('..', __dir__)
destination = File.expand_path(ARGV.first)
Dir.mktmpdir('dt-layout-fixtures-') do |source|
  source = File.realpath(source)
  %w[_layouts _includes].each do |directory|
    FileUtils.cp_r(File.join(root, directory), source)
  end
  Dir.children(File.join(root, 'tests/fixtures')).each do |entry|
    FileUtils.cp_r(File.join(root, 'tests/fixtures', entry), source)
  end
  config = Jekyll.configuration(
    'source' => source,
    'destination' => destination,
    'config' => File.join(source, '_config.yml'),
    'safe' => true,
    'quiet' => true,
    'future' => true,
    'time' => Time.utc(2020, 1, 5, 12)
  )
  Jekyll::Site.new(config).process
end
