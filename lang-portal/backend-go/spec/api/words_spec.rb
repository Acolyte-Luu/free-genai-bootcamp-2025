require_relative '../spec_helper'

RSpec.describe 'Words API' do
  include ApiHelper

  describe 'GET /words' do
    it 'returns a paginated list of words' do
      response = get('/words', page: 1, limit: 10)
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body).to have_key('data')
      expect(body).to have_key('pagination')
      
      # Check word structure
      word = body['data'].first
      expect(word).to include(
        'id',
        'japanese',
        'romaji',
        'english',
        'correct_count',
        'incorrect_count',
        'created_at'
      )

      # Check pagination structure
      expect(body['pagination']).to include(
        'current_page',
        'total_pages',
        'total_items',
        'items_per_page'
      )
    end
  end

  describe 'GET /words/:id' do
    it 'returns a single word with its groups' do
      response = get('/words/1')
      body = JSON.parse(response.body)

      expect(response.code).to eq(200)
      expect(body).to have_key('data')
      expect(body).to have_key('groups')

      word = body['data']
      expect(word).to include(
        'id',
        'japanese',
        'romaji',
        'english',
        'created_at'
      )
    end
  end

  context 'error cases' do
    it 'returns 404 for non-existent word' do
      response = get('/words/999999')
      body = JSON.parse(response.body)

      expect(response.code).to eq(404)
      expect(body['success']).to be false
      expect(body['error']).to eq('Word not found')
    end

    it 'returns 400 for invalid word ID' do
      response = get('/words/invalid')
      body = JSON.parse(response.body)

      expect(response.code).to eq(400)
      expect(body['success']).to be false
      expect(body['error']).to eq('Invalid word ID')
    end
  end
end 