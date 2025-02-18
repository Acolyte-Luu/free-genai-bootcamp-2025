require_relative '../spec_helper'

RSpec.describe 'Study Flow' do
  include ApiHelper

  let(:study_session) { nil }

  before(:each) do
    # Create a new study session before each test
    response = post('/study_activities', {
      group_id: 1,
      study_activity_id: 1
    })
    @study_session = JSON.parse(response.body)['data']['study_session_id']
  end

  it 'completes a full study session flow' do
    # 1. Start study session
    expect(@study_session).not_to be_nil

    # 2. Review some words
    response = post("/study_sessions/#{@study_session}/words/1/review", {
      correct: true
    })
    expect(response.code).to eq(200)

    # 3. Check session progress
    response = get("/study_sessions/#{@study_session}")
    body = JSON.parse(response.body)
    expect(body['data']['review_items_count']).to eq(1)

    # 4. Verify dashboard updates
    response = get('/dashboard/last_study_session')
    body = JSON.parse(response.body)
    expect(body['data']['id']).to eq(@study_session)
    expect(body['data']['correct_count']).to eq(1)
  end
end 