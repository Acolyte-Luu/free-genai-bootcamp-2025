require_relative '../spec_helper'

RSpec.describe 'Groups API' do
  include ApiHelper

  describe 'GET /groups' do
    it 'returns a paginated list of groups' do
      response = get('/groups', page: 1, limit: 10)
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body).to have_key('data')
      expect(body).to have_key('pagination')

      group = body['data'].first
      expect(group).to include(
        'id',
        'name',
        'created_at'
      )
    end
  end

  describe 'GET /groups/:id' do
    it 'returns a single group with stats' do
      response = get('/groups/1')
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body['data']).to include(
        'id',
        'name',
        'total_word_count'
      )
    end
  end

  describe 'GET /groups/:id/words' do
    it 'returns words in the group with stats' do
      response = get('/groups/1/words', page: 1, limit: 10)
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body).to have_key('success')
      expect(body['success']).to be true
      expect(body['data']).to have_key('data')
      
      word = body['data']['data'].first
      expect(word).to include(
        'japanese',
        'romaji',
        'english',
        'correct_count',
        'incorrect_count'
      )
    end
  end
end 