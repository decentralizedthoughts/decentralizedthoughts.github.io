#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "net/http"
require "openssl"
require "stringio"
require "time"
require "uri"
require "base64"
require "pathname"

SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
TOKEN_URI = URI("https://oauth2.googleapis.com/token")
REPORT_URI_TEMPLATE = "https://analyticsdata.googleapis.com/v1beta/properties/%<property>s:runReport"
OUTPUT_PATH = Pathname.new(__dir__).join("..", "assets", "data", "top-pages.json").expand_path
EXCLUDED_PREFIXES = %w[
  /about-
  /authors/
  /assets/
  /feed.xml
  /favicon.ico
  /page
  /tag/
  /tags
].freeze

EXCLUDED_EXACT_PATHS = %w[
  /
  /404.html
  /contents/
].freeze

def b64url(value)
  Base64.urlsafe_encode64(value).delete("=")
end

def write_output(payload)
  OUTPUT_PATH.write(JSON.pretty_generate(payload) + "\n")
end

def service_account_data
  inline = ENV["GA4_SERVICE_ACCOUNT_JSON"] || ENV["GOOGLE_SERVICE_ACCOUNT_JSON"]
  return JSON.parse(inline) if inline && !inline.strip.empty?

  path = ENV["GA4_SERVICE_ACCOUNT_JSON_PATH"] || ENV["GOOGLE_APPLICATION_CREDENTIALS"]
  return JSON.parse(File.read(path)) if path && File.exist?(path)

  nil
end

def build_jwt_assertion(service_account)
  now = Time.now.to_i
  header = { alg: "RS256", typ: "JWT" }
  claim_set = {
    iss: service_account.fetch("client_email"),
    scope: SCOPE,
    aud: TOKEN_URI.to_s,
    exp: now + 3600,
    iat: now
  }

  signing_input = [header, claim_set].map { |part| b64url(JSON.generate(part)) }.join(".")
  private_key = OpenSSL::PKey::RSA.new(service_account.fetch("private_key"))
  signature = private_key.sign(OpenSSL::Digest::SHA256.new, signing_input)
  [signing_input, b64url(signature)].join(".")
end

def fetch_access_token
  direct_token = ENV["GA4_ACCESS_TOKEN"]
  return direct_token if direct_token && !direct_token.strip.empty?

  service_account = service_account_data
  raise "missing GA4 credentials" unless service_account

  request = Net::HTTP::Post.new(TOKEN_URI)
  request.set_form_data(
    "grant_type" => "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion" => build_jwt_assertion(service_account)
  )

  response = Net::HTTP.start(TOKEN_URI.host, TOKEN_URI.port, use_ssl: true) do |http|
    http.request(request)
  end
  raise "token request failed: #{response.code} #{response.body}" unless response.is_a?(Net::HTTPSuccess)

  JSON.parse(response.body).fetch("access_token")
end

def fetch_top_pages(access_token, property_id, limit)
  uri = URI(format(REPORT_URI_TEMPLATE, property: property_id))
  request = Net::HTTP::Post.new(uri)
  request["Authorization"] = "Bearer #{access_token}"
  request["Content-Type"] = "application/json"
  request.body = JSON.generate(
    dateRanges: [{ startDate: ENV.fetch("GA4_START_DATE", "28daysAgo"), endDate: ENV.fetch("GA4_END_DATE", "yesterday") }],
    dimensions: [{ name: "unifiedPagePathScreen" }],
    metrics: [{ name: "screenPageViews" }],
    orderBys: [{ metric: { metricName: "screenPageViews" }, desc: true }],
    dimensionFilter: {
      filter: {
        fieldName: "unifiedPagePathScreen",
        stringFilter: {
          matchType: "BEGINS_WITH",
          value: "/"
        }
      }
    },
    limit: limit
  )

  response = Net::HTTP.start(uri.host, uri.port, use_ssl: true) do |http|
    http.request(request)
  end
  raise "report request failed: #{response.code} #{response.body}" unless response.is_a?(Net::HTTPSuccess)

  JSON.parse(response.body)
end

def normalize_items(rows)
  rows.filter_map do |row|
    path = row.fetch("dimensionValues", []).dig(0, "value").to_s.strip
    views = row.fetch("metricValues", []).dig(0, "value").to_i
    next if path.empty?

    canonical_path = path.end_with?("/") ? path : "#{path}/"
    next if EXCLUDED_EXACT_PATHS.include?(path) || EXCLUDED_EXACT_PATHS.include?(canonical_path)
    next if EXCLUDED_PREFIXES.any? { |prefix| path.start_with?(prefix) || canonical_path.start_with?(prefix) }

    {
      "path" => canonical_path,
      "views" => views
    }
  end
end

begin
  property_id = ENV.fetch("GA4_PROPERTY_ID")
  limit = Integer(ENV.fetch("GA4_TOP_PAGES_LIMIT", "8"))
  access_token = fetch_access_token
  report = fetch_top_pages(access_token, property_id, limit)
  items = normalize_items(report.fetch("rows", []))

  write_output(
    {
      "source" => "ga4",
      "fetched_at" => Time.now.utc.iso8601,
      "items" => items
    }
  )
rescue StandardError => e
  warn "GA top pages refresh failed: #{e.message}"
  write_output(
    {
      "source" => "fallback",
      "fetched_at" => nil,
      "items" => []
    }
  )
  exit 1 if ENV["GA4_STRICT"] == "1"
end
