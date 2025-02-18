require_relative '../spec_helper'

RSpec.describe 'Reset API' do
  include ApiHelper

  describe 'POST /reset_history' do
    it 'resets study history while preserving words and groups' do
      # First create some study data
      response = post('/study_activities', {
        group_id: 1,
        study_activity_id: 1
      })
      expect(response.code).to eq(201)

      # Reset history
      response = post('/reset_history')
      expect(response.code).to eq(200)
      expect(JSON.parse(response.body)['success']).to be true

      # Verify study data is gone but words remain
      response = get('/dashboard/study_progress')
      body = JSON.parse(response.body)
      expect(body['data']['total_words_studied']).to eq(0)

      response = get('/words')
      body = JSON.parse(response.body)
      expect(body['data'].length).to be > 0
    end
  end

  describe 'POST /full_reset' do
    it 'resets all application data' do
      response = post('/full_reset')
      body = JSON.parse(response.body)
      puts "Response Body: #{response.body}"
      puts "Parsed Body: #{body.inspect}"
      puts "Data: #{body['data'].inspect}"
      expect(body['data'].length).to eq(0)
    end
  end
end 