require_relative '../spec_helper'

RSpec.describe 'Study Sessions API' do
  include ApiHelper

  describe 'POST /study_activities' do
    it 'creates a new study session' do
      response = post('/study_activities', {
        group_id: 1,
        study_activity_id: 1
      })
      body = JSON.parse(response.body)

      expect(response.code).to eq(201)
      expect(body['data']).to include(
        'study_session_id',
        'group_id'
      )
    end
  end

  describe 'POST /study_sessions/:id/words/:word_id/review' do
    it 'records a word review' do
      response = post('/study_sessions/1/words/1/review', {
        correct: true
      })
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body['success']).to be true
      expect(body['data']).to include(
        'word_id',
        'study_session_id',
        'correct'
      )
    end
  end
end 