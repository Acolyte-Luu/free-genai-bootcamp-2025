def fix_vocabulary_format(data):
    """Ensure all vocabulary items have the required fields including parts."""
    if not data or not isinstance(data, dict):
        return data
        
    # If this is the final answer with vocabulary
    if "final_answer" in data and isinstance(data["final_answer"], dict):
        final_answer = data["final_answer"]
        
        # Add vocabulary field if it's missing entirely
        if "vocabulary" not in final_answer or not isinstance(final_answer["vocabulary"], list):
            print("Adding missing vocabulary field")
            final_answer["vocabulary"] = [
                {
                    "kanji": "愛",
                    "romaji": "ai",
                    "english": "love",
                    "parts": [
                        {
                            "kanji": "愛",
                            "romaji": ["ai"]
                        }
                    ]
                }
            ]
        
        # If it has vocabulary items
        if "vocabulary" in final_answer and isinstance(final_answer["vocabulary"], list):
            for i, item in enumerate(final_answer["vocabulary"]):
                # Ensure each item has kanji, romaji, english
                if "kanji" not in item or not item["kanji"]:
                    item["kanji"] = f"未知{i+1}"  # Unknown + number
                
                if "romaji" not in item or not item["romaji"]:
                    if "kanji" in item and item["kanji"]:
                        item["romaji"] = item["kanji"]  # Use kanji as fallback
                    else:
                        item["romaji"] = f"michi{i+1}"  # Unknown in romaji
                
                if "english" not in item or not item["english"]:
                    item["english"] = f"unknown term {i+1}"
                
                # Add parts if missing
                if "parts" not in item or not isinstance(item["parts"], list) or not item["parts"]:
                    # Create a simple part from the whole word
                    item["parts"] = [{
                        "kanji": item["kanji"],
                        "romaji": [item["romaji"] if isinstance(item["romaji"], str) else item["romaji"][0]]
                    }]
                    
                # Ensure each part has required fields
                for part in item["parts"]:
                    if "kanji" not in part or not part["kanji"]:
                        part["kanji"] = item["kanji"]
                    
                    if "romaji" not in part or not part["romaji"]:
                        if isinstance(item["romaji"], list):
                            part["romaji"] = item["romaji"]
                        else:
                            part["romaji"] = [item["romaji"]]
    
    return data 