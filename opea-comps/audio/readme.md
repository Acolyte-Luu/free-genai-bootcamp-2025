# Test with 1-minute sample
curl -X POST "http://127.0.0.1:9880" \
-H "Content-Type: application/json" \
-d @- \
--output output-1m.wav << 'EOF'
{
    "refer_wav_path": "/audio/1minsample-new.wav",
    "prompt_text": "Welcome to this guided meditation on finding inner peace. Take a deep breath in through your nose, feeling your chest expand. And release it slowly through your mouth. Imagine yourself standing on a quiet beach at sunrise.",
    "prompt_language": "en",
    "text": "This is latest sentence I want to convert to speech",
    "text_language": "en"
}
EOF


# Test with 10-second sample
curl -X POST "http://127.0.0.1:9880" \
-H "Content-Type: application/json" \
-d @- \
--output output-10s.wav << 'EOF'
{
    "refer_wav_path": "/audio/1minsample-new.wav",
    "prompt_text": "Because there's so much snow outside, I think I won't go to the office today and what I'll do instead is stay indoors and make myself some hamburgers and pizza. Does anyone like that idea?",
    "prompt_language": "en",
    "text": "This is a new sentence I want to convert to speech",
    "text_language": "en"
}
EOF