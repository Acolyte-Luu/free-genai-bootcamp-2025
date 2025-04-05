"""
Template quests for JP-MUD
"""

from app.models.quest import ObjectiveType, RewardType

DEFAULT_QUESTS = [
    {
        "id": "quest_village_map",
        "title": "The Village Map",
        "japanese_title": "村の地図",
        "description": "Find the old map that shows the layout of the village and surrounding areas.",
        "japanese_description": "村と周辺地域のレイアウトを示す古い地図を見つけてください。",
        "objectives": [
            {
                "id": "objective_find_map",
                "type": ObjectiveType.COLLECT_ITEM,
                "description": "Find the village map",
                "japanese_description": "村の地図を見つける",
                "target_id": "map",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "地図",
                        "english": "map",
                        "reading": "ちず"
                    },
                    {
                        "japanese": "探す",
                        "english": "to search, to look for",
                        "reading": "さがす"
                    }
                ]
            }
        ],
        "rewards": [
            {
                "type": RewardType.VOCABULARY_BOOST,
                "description": "Learn map-related vocabulary",
                "japanese_description": "地図に関連する語彙を学ぶ",
                "vocabulary": [
                    {
                        "japanese": "方向",
                        "english": "direction",
                        "reading": "ほうこう"
                    },
                    {
                        "japanese": "場所",
                        "english": "place, location",
                        "reading": "ばしょ"
                    }
                ]
            }
        ],
        "prerequisite_quests": [],
        "start_location": "start",
        "completion_location": None,
        "difficulty": 1,
        "jlpt_level": 5,
        "hidden": False
    },
    {
        "id": "quest_talk_to_elder",
        "title": "Village Wisdom",
        "japanese_title": "村の知恵",
        "description": "Speak to the village elder to learn about the area's history.",
        "japanese_description": "地域の歴史について学ぶために村長と話してください。",
        "objectives": [
            {
                "id": "objective_talk_to_elder",
                "type": ObjectiveType.TALK_TO_NPC,
                "description": "Speak to the village elder",
                "japanese_description": "村長と話す",
                "target_id": "elder",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "村長",
                        "english": "village elder",
                        "reading": "そんちょう"
                    },
                    {
                        "japanese": "話す",
                        "english": "to speak, to talk",
                        "reading": "はなす"
                    }
                ]
            }
        ],
        "rewards": [
            {
                "type": RewardType.UNLOCK_LOCATION,
                "description": "Learn about a secret path",
                "japanese_description": "秘密の道について学ぶ",
                "target_id": "hidden_path"
            }
        ],
        "prerequisite_quests": ["quest_village_map"],
        "start_location": None,
        "completion_location": None,
        "difficulty": 1,
        "jlpt_level": 5,
        "hidden": False
    },
    {
        "id": "quest_shrine_offering",
        "title": "Shrine Offering",
        "japanese_title": "神社のお供え",
        "description": "Bring an offering to the mountain shrine to receive a blessing.",
        "japanese_description": "祝福を受けるために山の神社にお供えを持って行きましょう。",
        "objectives": [
            {
                "id": "objective_get_offering",
                "type": ObjectiveType.COLLECT_ITEM,
                "description": "Obtain a suitable offering",
                "japanese_description": "適切なお供えを手に入れる",
                "target_id": "offering",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "お供え",
                        "english": "offering",
                        "reading": "おそなえ"
                    }
                ]
            },
            {
                "id": "objective_visit_shrine",
                "type": ObjectiveType.VISIT_LOCATION,
                "description": "Visit the mountain shrine",
                "japanese_description": "山の神社を訪れる",
                "target_id": "shrine",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "神社",
                        "english": "shrine",
                        "reading": "じんじゃ"
                    },
                    {
                        "japanese": "訪れる",
                        "english": "to visit",
                        "reading": "おとずれる"
                    }
                ]
            },
            {
                "id": "objective_talk_to_priest",
                "type": ObjectiveType.TALK_TO_NPC,
                "description": "Speak with the shrine priest",
                "japanese_description": "神主と話す",
                "target_id": "priest",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "神主",
                        "english": "shrine priest",
                        "reading": "かんぬし"
                    }
                ]
            }
        ],
        "rewards": [
            {
                "type": RewardType.ITEM,
                "description": "Receive a protective charm",
                "japanese_description": "お守りを受け取る",
                "target_id": "omamori"
            },
            {
                "type": RewardType.VOCABULARY_BOOST,
                "description": "Learn shrine-related vocabulary",
                "japanese_description": "神社に関連する語彙を学ぶ",
                "vocabulary": [
                    {
                        "japanese": "祝福",
                        "english": "blessing",
                        "reading": "しゅくふく"
                    },
                    {
                        "japanese": "お参り",
                        "english": "worship, visiting a shrine",
                        "reading": "おまいり"
                    },
                    {
                        "japanese": "拝む",
                        "english": "to worship, to pray",
                        "reading": "おがむ"
                    }
                ]
            }
        ],
        "prerequisite_quests": ["quest_talk_to_elder"],
        "start_location": None,
        "completion_location": "shrine",
        "difficulty": 2,
        "jlpt_level": 5,
        "hidden": False
    },
    {
        "id": "quest_fishing",
        "title": "Fishing Lesson",
        "japanese_title": "釣りのレッスン",
        "description": "Learn how to fish at the river.",
        "japanese_description": "川で釣り方を学びましょう。",
        "objectives": [
            {
                "id": "objective_get_fishing_rod",
                "type": ObjectiveType.COLLECT_ITEM,
                "description": "Get a fishing rod",
                "japanese_description": "釣り竿を手に入れる",
                "target_id": "fishing_rod",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "釣り竿",
                        "english": "fishing rod",
                        "reading": "つりざお"
                    }
                ]
            },
            {
                "id": "objective_go_to_river",
                "type": ObjectiveType.VISIT_LOCATION,
                "description": "Go to the river",
                "japanese_description": "川に行く",
                "target_id": "river",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "川",
                        "english": "river",
                        "reading": "かわ"
                    }
                ]
            },
            {
                "id": "objective_use_fishing_rod",
                "type": ObjectiveType.USE_ITEM,
                "description": "Use the fishing rod at the river",
                "japanese_description": "川で釣り竿を使う",
                "target_id": "fishing_rod",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "釣る",
                        "english": "to fish",
                        "reading": "つる"
                    },
                    {
                        "japanese": "使う",
                        "english": "to use",
                        "reading": "つかう"
                    }
                ]
            }
        ],
        "rewards": [
            {
                "type": RewardType.ITEM,
                "description": "Catch a fish",
                "japanese_description": "魚を捕まえる",
                "target_id": "fish"
            },
            {
                "type": RewardType.VOCABULARY_BOOST,
                "description": "Learn fishing-related vocabulary",
                "japanese_description": "釣りに関連する語彙を学ぶ",
                "vocabulary": [
                    {
                        "japanese": "魚",
                        "english": "fish",
                        "reading": "さかな"
                    },
                    {
                        "japanese": "釣り",
                        "english": "fishing",
                        "reading": "つり"
                    },
                    {
                        "japanese": "餌",
                        "english": "bait",
                        "reading": "えさ"
                    }
                ]
            }
        ],
        "prerequisite_quests": [],
        "start_location": "river",
        "completion_location": "river",
        "difficulty": 1,
        "jlpt_level": 5,
        "hidden": False
    },
    {
        "id": "quest_lantern_night",
        "title": "Lantern Night",
        "japanese_title": "提灯の夜",
        "description": "Find a lantern to help navigate in the dark areas.",
        "japanese_description": "暗い場所を案内するために提灯を見つけましょう。",
        "objectives": [
            {
                "id": "objective_find_lantern",
                "type": ObjectiveType.COLLECT_ITEM,
                "description": "Find a paper lantern",
                "japanese_description": "提灯を見つける",
                "target_id": "lantern",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "提灯",
                        "english": "paper lantern",
                        "reading": "ちょうちん"
                    },
                    {
                        "japanese": "明かり",
                        "english": "light",
                        "reading": "あかり"
                    }
                ]
            },
            {
                "id": "objective_use_lantern",
                "type": ObjectiveType.USE_ITEM,
                "description": "Use the lantern in a dark place",
                "japanese_description": "暗い場所で提灯を使う",
                "target_id": "lantern",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "暗い",
                        "english": "dark",
                        "reading": "くらい"
                    },
                    {
                        "japanese": "場所",
                        "english": "place",
                        "reading": "ばしょ"
                    }
                ]
            }
        ],
        "rewards": [
            {
                "type": RewardType.UNLOCK_LOCATION,
                "description": "Discover a hidden cave",
                "japanese_description": "隠された洞窟を発見する",
                "target_id": "cave"
            },
            {
                "type": RewardType.VOCABULARY_BOOST,
                "description": "Learn light-related vocabulary",
                "japanese_description": "光に関連する語彙を学ぶ",
                "vocabulary": [
                    {
                        "japanese": "光",
                        "english": "light (noun)",
                        "reading": "ひかり"
                    },
                    {
                        "japanese": "輝く",
                        "english": "to shine",
                        "reading": "かがやく"
                    },
                    {
                        "japanese": "闇",
                        "english": "darkness",
                        "reading": "やみ"
                    }
                ]
            }
        ],
        "prerequisite_quests": ["quest_talk_to_elder"],
        "start_location": None,
        "completion_location": None,
        "difficulty": 2,
        "jlpt_level": 5,
        "hidden": False
    },
    {
        "id": "quest_particle_practice",
        "title": "Particles Practice",
        "japanese_title": "助詞の練習",
        "description": "Practice using Japanese particles correctly in various contexts.",
        "japanese_description": "様々な状況で日本語の助詞を正しく使う練習をしましょう。",
        "objectives": [
            {
                "id": "objective_wa_ga_practice",
                "type": ObjectiveType.GRAMMAR_CHALLENGE,
                "description": "Practice using は and が correctly",
                "japanese_description": "「は」と「が」を正しく使う練習",
                "target_id": "wa_ga_challenge",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "は",
                        "english": "topic marker particle",
                        "reading": "は"
                    },
                    {
                        "japanese": "が",
                        "english": "subject marker particle",
                        "reading": "が"
                    }
                ],
                "properties": {
                    "prompt": "Complete the sentence: 私___日本語を勉強しています。(I am studying Japanese.)",
                    "correct_pattern": "私は日本語を勉強しています",
                    "use_pattern": True,
                    "hint": "Use は to mark the topic of the sentence.",
                    "grammar_point": {
                        "name": "Topic marker は vs Subject marker が",
                        "explanation": "は (wa) marks the topic of a sentence, while が (ga) marks the subject. は often introduces what the sentence is about, while が emphasizes who or what is doing the action.",
                        "examples": [
                            {"japanese": "私は学生です", "english": "I am a student (topic)"},
                            {"japanese": "私が学生です", "english": "I am the student (subject, distinguishing from others)"}
                        ]
                    }
                }
            },
            {
                "id": "objective_wo_practice",
                "type": ObjectiveType.GRAMMAR_CHALLENGE,
                "description": "Practice using を correctly",
                "japanese_description": "「を」を正しく使う練習",
                "target_id": "wo_challenge",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "を",
                        "english": "direct object marker particle",
                        "reading": "を"
                    }
                ],
                "properties": {
                    "prompt": "Complete the sentence: 私は本___読みます。(I read a book.)",
                    "correct_pattern": "私は本を読みます",
                    "use_pattern": True,
                    "hint": "Use を to mark the direct object of the action.",
                    "grammar_point": {
                        "name": "Object marker を",
                        "explanation": "を (wo) marks the direct object of a verb - the thing that receives the action.",
                        "examples": [
                            {"japanese": "水を飲みます", "english": "I drink water"},
                            {"japanese": "映画を見ます", "english": "I watch a movie"}
                        ]
                    }
                }
            }
        ],
        "rewards": [
            {
                "type": RewardType.VOCABULARY_BOOST,
                "description": "Learn particle-related vocabulary",
                "japanese_description": "助詞に関連する語彙を学ぶ",
                "vocabulary": [
                    {
                        "japanese": "助詞",
                        "english": "particle",
                        "reading": "じょし"
                    },
                    {
                        "japanese": "文法",
                        "english": "grammar",
                        "reading": "ぶんぽう"
                    }
                ]
            }
        ],
        "prerequisite_quests": ["quest_talk_to_elder"],
        "start_location": None,
        "completion_location": None,
        "difficulty": 2,
        "jlpt_level": 5,
        "hidden": False
    },
    {
        "id": "quest_verb_forms",
        "title": "Verb Transformations",
        "japanese_title": "動詞の変形",
        "description": "Learn to transform Japanese verbs into their different forms.",
        "japanese_description": "日本語の動詞をさまざまな形に変える練習をしましょう。",
        "objectives": [
            {
                "id": "objective_masu_form",
                "type": ObjectiveType.GRAMMAR_CHALLENGE,
                "description": "Change verbs to polite form (ます form)",
                "japanese_description": "動詞を丁寧形（ます形）に変える",
                "target_id": "masu_form_challenge",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "ます",
                        "english": "polite form suffix",
                        "reading": "ます"
                    }
                ],
                "properties": {
                    "prompt": "Change this verb to the polite form: 食べる → ?",
                    "correct_pattern": "食べます",
                    "use_pattern": False,
                    "hint": "For る-verbs, remove る and add ます",
                    "grammar_point": {
                        "name": "Polite form (ます form)",
                        "explanation": "The ます form is used in polite speech. For る-verbs, remove る and add ます. For う-verbs, change the final う sound to い sound and add ます.",
                        "examples": [
                            {"japanese": "食べる → 食べます", "english": "eat → eat (polite)"},
                            {"japanese": "飲む → 飲みます", "english": "drink → drink (polite)"}
                        ]
                    }
                }
            },
            {
                "id": "objective_negative_form",
                "type": ObjectiveType.GRAMMAR_CHALLENGE,
                "description": "Change verbs to negative polite form",
                "japanese_description": "動詞を否定の丁寧形に変える",
                "target_id": "negative_form_challenge",
                "count": 1,
                "vocabulary": [
                    {
                        "japanese": "ません",
                        "english": "negative polite form suffix",
                        "reading": "ません"
                    }
                ],
                "properties": {
                    "prompt": "Change this verb to the negative polite form: 食べる → ?",
                    "correct_pattern": "食べません",
                    "use_pattern": False,
                    "hint": "For る-verbs, remove る and add ません",
                    "grammar_point": {
                        "name": "Negative polite form (ません form)",
                        "explanation": "To make a verb negative in the polite form, replace ます with ません.",
                        "examples": [
                            {"japanese": "食べます → 食べません", "english": "eat (polite) → don't eat (polite)"},
                            {"japanese": "飲みます → 飲みません", "english": "drink (polite) → don't drink (polite)"}
                        ]
                    }
                }
            }
        ],
        "rewards": [
            {
                "type": RewardType.VOCABULARY_BOOST,
                "description": "Learn verb-related vocabulary",
                "japanese_description": "動詞に関連する語彙を学ぶ",
                "vocabulary": [
                    {
                        "japanese": "動詞",
                        "english": "verb",
                        "reading": "どうし"
                    },
                    {
                        "japanese": "変形",
                        "english": "transformation",
                        "reading": "へんけい"
                    },
                    {
                        "japanese": "丁寧形",
                        "english": "polite form",
                        "reading": "ていねいけい"
                    }
                ]
            }
        ],
        "prerequisite_quests": ["quest_particle_practice"],
        "start_location": None,
        "completion_location": None,
        "difficulty": 3,
        "jlpt_level": 5,
        "hidden": False
    }
]

# Additional item needed for quests
QUEST_ITEMS = [
    {
        "id": "offering",
        "name": "Rice Offering",
        "japanese_name": "お米のお供え",
        "description": "A small bundle of rice wrapped in bamboo leaves, suitable as an offering at a shrine.",
        "japanese_description": "笹の葉に包まれた小さなお米の束。神社へのお供えに適しています。",
        "type": "quest",
        "location": "house",
        "properties": {},
        "vocabulary": [
            {"japanese": "お米", "english": "rice", "reading": "おこめ"},
            {"japanese": "笹の葉", "english": "bamboo leaf", "reading": "ささのは"},
            {"japanese": "束", "english": "bundle", "reading": "たば"}
        ],
        "can_be_taken": True,
        "hidden": False,
        "related_quest_id": "quest_shrine_offering"
    },
    {
        "id": "fish",
        "name": "Fresh Fish",
        "japanese_name": "新鮮な魚",
        "description": "A small, freshly caught fish from the river.",
        "japanese_description": "川から釣ったばかりの小さな新鮮な魚。",
        "type": "quest",
        "location": None,  # This is a reward, not placed in the world
        "properties": {
            "use_effect": "You cook and eat the fish. It's delicious!"
        },
        "vocabulary": [
            {"japanese": "新鮮", "english": "fresh", "reading": "しんせん"},
            {"japanese": "料理する", "english": "to cook", "reading": "りょうりする"},
            {"japanese": "美味しい", "english": "delicious", "reading": "おいしい"}
        ],
        "can_be_taken": True,
        "hidden": False,
        "related_quest_id": "quest_fishing"
    }
]

# Hidden locations unlocked through quests
HIDDEN_LOCATIONS = [
    {
        "id": "hidden_path",
        "name": "Hidden Forest Path",
        "japanese_name": "隠れた森の道",
        "description": "A narrow path through the bamboo forest that few know about. It leads deeper into the mountains.",
        "japanese_description": "竹林を通る狭い道で、知る人ぞ知る道です。山の奥へと続いています。",
        "connections": {
            "north": "mountain",
            "south": "forest"
        },
        "vocabulary": [
            {"japanese": "隠れた", "english": "hidden", "reading": "かくれた"},
            {"japanese": "狭い", "english": "narrow", "reading": "せまい"},
            {"japanese": "奥", "english": "inner part, deep", "reading": "おく"}
        ],
        "visited": False,
        "hidden": True
    },
    {
        "id": "cave",
        "name": "Mountain Cave",
        "japanese_name": "山の洞窟",
        "description": "A dark cave in the mountain, illuminated by your lantern. Strange crystals glitter on the walls.",
        "japanese_description": "山にある暗い洞窟で、あなたの提灯に照らされています。壁には奇妙な結晶がきらめいています。",
        "connections": {
            "out": "mountain"
        },
        "vocabulary": [
            {"japanese": "洞窟", "english": "cave", "reading": "どうくつ"},
            {"japanese": "結晶", "english": "crystal", "reading": "けっしょう"},
            {"japanese": "きらめく", "english": "to glitter, to sparkle", "reading": "きらめく"}
        ],
        "visited": False,
        "hidden": True
    }
] 