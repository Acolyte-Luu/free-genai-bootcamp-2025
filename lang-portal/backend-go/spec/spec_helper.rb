require 'rspec'
require 'httparty'
require 'json'
require 'amazing_print'

# Set test environment
ENV['GO_ENV'] = 'test'

# API Helper module
module ApiHelper
  BASE_URL = 'http://localhost:8080/api'

  module_function  # This makes the methods accessible as module methods

  def get(path, params = {})
    response = HTTParty.get("#{BASE_URL}#{path}", query: params)
    puts "\nGET #{path} Response: #{response.body}" if response.code != 200
    response
  end

  def post(path, body = {})
    response = HTTParty.post(
      "#{BASE_URL}#{path}",
      body: body.to_json,
      headers: { 'Content-Type' => 'application/json' }
    )
    puts "\nPOST #{path} Response: #{response.body}" if response.code != 201
    response
  end

  def reset_database
    post('/reset_history')
    post('/full_reset')
  end

  def seed_database
    puts "\n=== Seeding Database ==="
    
    # First create a group
    group_response = post('/groups', {
      name: 'Test Group'
    })
    
    puts "Group creation response: #{group_response.body}"
    group_data = JSON.parse(group_response.body)
    group_id = group_data['data']['id']
    puts "Created group with ID: #{group_id}"

    # Then create words in that group
    words_response = post("/groups/#{group_id}/words", {
      words: [
        {
          japanese: 'テスト',
          romaji: 'tesuto',
          english: 'test'
        }
      ]
    })
    
    puts "Words creation response: #{words_response.body}"
    words_data = JSON.parse(words_response.body)
    puts "Created words: #{words_data['data'].inspect}"
    puts "=== Seeding Complete ===\n"
  end

  def verify_database
    puts "\n=== Verifying Database Content ==="
    
    groups_response = get('/groups')
    puts "Groups in database: #{groups_response.body}"
    
    words_response = get('/words')
    puts "Words in database: #{words_response.body}"
    puts "=== Verification Complete ===\n"
  end
end

RSpec.configure do |config|
  config.expect_with :rspec do |expectations|
    expectations.include_chain_clauses_in_custom_matcher_descriptions = true
  end

  config.mock_with :rspec do |mocks|
    mocks.verify_partial_doubles = true
  end

  config.shared_context_metadata_behavior = :apply_to_host_groups

  config.before(:suite) do
    ApiHelper.reset_database
    ApiHelper.seed_database
    ApiHelper.verify_database
  end
end 