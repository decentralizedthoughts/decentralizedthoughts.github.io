#!/usr/bin/env ruby
require 'date'
require 'yaml'

# Match the date-and-slug permalink, including front matter date overrides.
posts = Dir['_posts/*.{md,markdown}'].map do |path|
  front_matter = File.read(path).split(/^---\s*$\n?/, 3)[1]
  next unless front_matter
  metadata = YAML.safe_load(front_matter, permitted_classes: [Date, Time], aliases: true) || {}
  slug = File.basename(path).sub(/\.(md|markdown)$/, '').sub(/^\d{4}-\d{2}-\d{2}-/, '').gsub(/\s+/, '-')
  date = DateTime.parse(metadata.fetch('date').to_s).strftime('%Y-%m-%d')
  ["/#{date}-#{slug}/", [path, metadata]]
end.compact.to_h
errors = []
posts.each do |url, (path, metadata)|
  %w[chapters background continue_reading].each do |field|
    next unless metadata.key?(field)
    links = metadata[field]
    unless links.is_a?(Array) && links.all? { |link| link.is_a?(String) }
      errors << "#{path}: #{field} must be a list of post URLs"
      next
    end
    errors << "#{path}: duplicate links in #{field}" unless links.uniq == links
    links.each do |target|
      errors << "#{path}: #{field} target does not exist: #{target}" unless posts.key?(target)
      errors << "#{path}: #{field} links to itself" if target == url
      if field == 'chapters' && posts.key?(target) && !posts[target][1]['title'].to_s.start_with?('Chapter:')
        errors << "#{path}: chapter target is not a chapter: #{target}"
      end
    end
  end
end
abort errors.join("\n") unless errors.empty?
puts 'OK: chapter and reading links reference existing posts'
