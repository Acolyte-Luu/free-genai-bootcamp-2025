VOCABULARY_EXTRACTION_PROMPT = """
Extract ALL vocabulary items from these lyrics that would be useful for language learners:

{lyrics}

For each vocabulary item, provide:
1. The word in its original form (kanji or kana)
2. The romaji (romanized pronunciation)
3. The English translation
4. Break down the word into its component parts with:
   - Each character or meaningful component (kanji)
   - The romanized reading(s) for each part as an array

Follow this exact format for each vocabulary item:
{
  "kanji": "いい",
  "romaji": "ii",
  "english": "good",
  "parts": [
    { "kanji": "い", "romaji": ["i"] },
    { "kanji": "い", "romaji": ["i"] }
  ]
}

Be comprehensive and include all unique words that would help someone learn the language.
If the lyrics are in English, translate key terms to Japanese.
Do not skip any words.
Make sure romaji is accurate for each part of the word.
""" 