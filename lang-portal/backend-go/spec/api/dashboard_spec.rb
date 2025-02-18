require_relative '../spec_helper'

RSpec.describe 'Dashboard API' do
  include ApiHelper

  describe 'GET /dashboard/last_study_session' do
    it 'returns the last study session details' do
      response = get('/dashboard/last_study_session')
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body['data']).to include(
        'id',
        'group_id',
        'group_name',
        'study_activity_id',
        'created_at',
        'correct_count',
        'total_words'
      )
    end
  end

  describe 'GET /dashboard/study_progress' do
    it 'returns study progress statistics' do
      response = get('/dashboard/study_progress')
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body['data']).to include(
        'total_words',
        'total_words_studied'
      )
    end
  end

  describe 'GET /dashboard/quick_stats' do
    it 'returns comprehensive statistics' do
      response = get('/dashboard/quick_stats')
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body['data']).to include(
        'total_study_sessions',
        'active_groups',
        'study_streak',
        'success_percentage'
      )

      stats = body['data']
      expect(stats['total_study_sessions']).to be >= 0
      expect(stats['active_groups']).to be >= 0
      expect(stats['study_streak']).to be >= 0
      expect(stats['success_percentage']).to be_between(0, 100)
    end
  end
end 