"""
Template world data for JP-MUD in case the LLM has issues generating a valid world.
"""

DEFAULT_WORLD = {
    "locations": [
        {
            "id": "start",
            "name": "Village Square",
            "japanese_name": "村の広場",
            "description": "A peaceful village square where your adventure begins. Cherry blossom trees line the edges, and a small fountain stands in the center.",
            "japanese_description": "あなたの冒険が始まる平和な村の広場です。桜の木が周りに並び、中央に小さな噴水があります。",
            "connections": {
                "north": "forest",
                "east": "shop",
                "west": "house",
                "south": "river"
            },
            "vocabulary": [
                {"japanese": "広場", "english": "square, plaza", "reading": "ひろば"},
                {"japanese": "村", "english": "village", "reading": "むら"},
                {"japanese": "桜", "english": "cherry blossom", "reading": "さくら"},
                {"japanese": "噴水", "english": "fountain", "reading": "ふんすい"}
            ]
        },
        {
            "id": "forest",
            "name": "Bamboo Forest",
            "japanese_name": "竹林",
            "description": "A dense forest of tall bamboo stalks. Sunlight filters through, creating patterns on the ground.",
            "japanese_description": "背の高い竹が密集している森。日光が地面に模様を作りながら差し込んでいます。",
            "connections": {
                "south": "start",
                "east": "shrine"
            },
            "vocabulary": [
                {"japanese": "竹", "english": "bamboo", "reading": "たけ"},
                {"japanese": "林", "english": "forest, woods", "reading": "はやし"},
                {"japanese": "日光", "english": "sunlight", "reading": "にっこう"},
                {"japanese": "地面", "english": "ground", "reading": "じめん"}
            ]
        },
        {
            "id": "shop",
            "name": "Old Shop",
            "japanese_name": "古い店",
            "description": "A traditional Japanese shop with wooden shelves full of various goods and curiosities.",
            "japanese_description": "様々な商品や珍品でいっぱいの木製の棚がある伝統的な日本の店。",
            "connections": {
                "west": "start"
            },
            "vocabulary": [
                {"japanese": "店", "english": "shop, store", "reading": "みせ"},
                {"japanese": "古い", "english": "old", "reading": "ふるい"},
                {"japanese": "棚", "english": "shelf", "reading": "たな"},
                {"japanese": "商品", "english": "goods, merchandise", "reading": "しょうひん"}
            ]
        },
        {
            "id": "house",
            "name": "Traditional House",
            "japanese_name": "伝統的な家",
            "description": "A beautiful traditional Japanese house with tatami floors and sliding paper doors.",
            "japanese_description": "畳の床と障子のある美しい伝統的な日本家屋。",
            "connections": {
                "east": "start"
            },
            "vocabulary": [
                {"japanese": "家", "english": "house, home", "reading": "いえ"},
                {"japanese": "伝統的", "english": "traditional", "reading": "でんとうてき"},
                {"japanese": "畳", "english": "tatami mat", "reading": "たたみ"},
                {"japanese": "障子", "english": "paper sliding door", "reading": "しょうじ"}
            ]
        },
        {
            "id": "river",
            "name": "Flowing River",
            "japanese_name": "流れる川",
            "description": "A clear, gentle river with small fish visible beneath the surface. A wooden bridge crosses to the other side.",
            "japanese_description": "澄んだ穏やかな川で、水面下に小さな魚が見えます。木製の橋が対岸へと渡っています。",
            "connections": {
                "north": "start",
                "south": "mountain"
            },
            "vocabulary": [
                {"japanese": "川", "english": "river", "reading": "かわ"},
                {"japanese": "流れる", "english": "to flow", "reading": "ながれる"},
                {"japanese": "橋", "english": "bridge", "reading": "はし"},
                {"japanese": "魚", "english": "fish", "reading": "さかな"}
            ]
        },
        {
            "id": "shrine",
            "name": "Mountain Shrine",
            "japanese_name": "山の神社",
            "description": "A serene shrine nestled among the trees. Stone lanterns line the path, and a red torii gate marks the entrance.",
            "japanese_description": "木々に囲まれた静かな神社。石灯籠が道に並び、赤い鳥居が入り口を示しています。",
            "connections": {
                "west": "forest"
            },
            "vocabulary": [
                {"japanese": "神社", "english": "shrine", "reading": "じんじゃ"},
                {"japanese": "鳥居", "english": "torii gate", "reading": "とりい"},
                {"japanese": "灯籠", "english": "stone lantern", "reading": "とうろう"},
                {"japanese": "静か", "english": "quiet, serene", "reading": "しずか"}
            ]
        },
        {
            "id": "mountain",
            "name": "Misty Mountain",
            "japanese_name": "霧の山",
            "description": "A tall mountain shrouded in mist. The path winds upward, disappearing into the clouds.",
            "japanese_description": "霧に包まれた高い山。道は上へと蛇行し、雲の中へと消えていきます。",
            "connections": {
                "north": "river"
            },
            "vocabulary": [
                {"japanese": "山", "english": "mountain", "reading": "やま"},
                {"japanese": "霧", "english": "mist, fog", "reading": "きり"},
                {"japanese": "雲", "english": "cloud", "reading": "くも"},
                {"japanese": "道", "english": "path, road", "reading": "みち"}
            ]
        }
    ],
    "characters": [
        {
            "id": "shopkeeper",
            "name": "Shopkeeper",
            "japanese_name": "店主",
            "description": "An elderly man with a warm smile, managing his shop with care and attention.",
            "japanese_description": "暖かい笑顔の老人で、店を丁寧に管理しています。",
            "location": "shop",
            "dialogues": {
                "default": {
                    "response": "Welcome to my humble shop! Please feel free to look around.",
                    "japanese_response": "私の小さな店へようこそ！どうぞごゆっくりご覧ください。"
                },
                "items": {
                    "response": "I have many interesting items for sale. The compass might be useful for your journey.",
                    "japanese_response": "色々と面白いものを売っています。その方位磁針はあなたの旅に役立つかもしれません。"
                },
                "village": {
                    "response": "This village has stood for centuries. The shrine to the north is especially sacred.",
                    "japanese_response": "この村は何世紀もの間存在しています。北にある神社は特に神聖な場所です。"
                }
            },
            "vocabulary": [
                {"japanese": "店主", "english": "shopkeeper", "reading": "てんしゅ"},
                {"japanese": "老人", "english": "elderly person", "reading": "ろうじん"},
                {"japanese": "笑顔", "english": "smile", "reading": "えがお"}
            ],
            "items": ["compass"],
            "quest_ids": []
        },
        {
            "id": "elder",
            "name": "Village Elder",
            "japanese_name": "村長",
            "description": "A wise old woman with deep knowledge of the local history and legends.",
            "japanese_description": "地元の歴史と伝説について深い知識を持つ賢い老女。",
            "location": "house",
            "dialogues": {
                "default": {
                    "response": "Greetings, young traveler. What brings you to our peaceful village?",
                    "japanese_response": "こんにちは、若い旅人さん。何があなたを私たちの平和な村に連れてきたのですか？"
                },
                "legend": {
                    "response": "There's an old legend about a sacred treasure hidden in the misty mountain. But beware, they say it's guarded by spirits.",
                    "japanese_response": "霧の山に隠された神聖な宝物についての古い伝説があります。でも気をつけて、精霊に守られていると言われています。"
                },
                "help": {
                    "response": "If you're planning to explore, you should speak with the shopkeeper. He sells useful items for adventurers.",
                    "japanese_response": "探検するつもりなら、店主と話すべきです。彼は冒険者に役立つアイテムを売っています。"
                }
            },
            "vocabulary": [
                {"japanese": "村長", "english": "village elder/chief", "reading": "そんちょう"},
                {"japanese": "伝説", "english": "legend", "reading": "でんせつ"},
                {"japanese": "宝物", "english": "treasure", "reading": "たからもの"}
            ],
            "items": [],
            "quest_ids": ["mountain_quest"]
        },
        {
            "id": "priest",
            "name": "Shrine Priest",
            "japanese_name": "神主",
            "description": "A solemn priest maintaining the mountain shrine, dressed in traditional white and blue robes.",
            "japanese_description": "伝統的な白と青の袍を着て、山の神社を管理している厳粛な神主。",
            "location": "shrine",
            "dialogues": {
                "default": {
                    "response": "Welcome to our sacred shrine. Please observe proper etiquette while visiting.",
                    "japanese_response": "私たちの神聖な神社へようこそ。参拝の際はマナーを守ってください。"
                },
                "prayer": {
                    "response": "To pray at the shrine, bow twice, clap your hands twice, then bow once more. This is called 'nirei nihakushu ichirei'.",
                    "japanese_response": "神社でお参りするには、二回お辞儀をして、二回手を叩いて、もう一度お辞儀をします。これを「二礼二拍手一礼」と言います。"
                },
                "blessing": {
                    "response": "I can offer you a blessing for your journey. This omamori will protect you from harm.",
                    "japanese_response": "あなたの旅のためにお祓いをすることができます。このお守りはあなたを危険から守るでしょう。"
                }
            },
            "vocabulary": [
                {"japanese": "神主", "english": "shrine priest", "reading": "かんぬし"},
                {"japanese": "お祓い", "english": "purification ritual", "reading": "おはらい"},
                {"japanese": "お守り", "english": "protective charm", "reading": "おまもり"}
            ],
            "items": ["omamori"],
            "quest_ids": []
        }
    ],
    "items": [
        {
            "id": "map",
            "name": "Village Map",
            "japanese_name": "村の地図",
            "description": "A hand-drawn map showing the village and surrounding areas.",
            "japanese_description": "村とその周辺地域を示す手書きの地図。",
            "type": "general",
            "location": "start",
            "properties": {},
            "vocabulary": [
                {"japanese": "地図", "english": "map", "reading": "ちず"},
                {"japanese": "手書き", "english": "hand-drawn", "reading": "てがき"}
            ],
            "can_be_taken": True,
            "hidden": False
        },
        {
            "id": "compass",
            "name": "Ancient Compass",
            "japanese_name": "古代の方位磁針",
            "description": "A beautifully crafted brass compass that always points toward your destination.",
            "japanese_description": "あなたの目的地に常に指を向ける、美しく作られた真鍮の方位磁針。",
            "type": "quest",
            "location": "shop",
            "properties": {
                "use_effect": "The compass needle spins and points toward the mountain."
            },
            "vocabulary": [
                {"japanese": "方位磁針", "english": "compass", "reading": "ほういじしん"},
                {"japanese": "真鍮", "english": "brass", "reading": "しんちゅう"}
            ],
            "can_be_taken": True,
            "hidden": False
        },
        {
            "id": "lantern",
            "name": "Paper Lantern",
            "japanese_name": "提灯",
            "description": "A traditional Japanese paper lantern that gives off a warm, soft light.",
            "japanese_description": "暖かく柔らかい光を放つ伝統的な日本の提灯。",
            "type": "general",
            "location": "house",
            "properties": {
                "use_effect": "The lantern illuminates the area, revealing hidden details."
            },
            "vocabulary": [
                {"japanese": "提灯", "english": "paper lantern", "reading": "ちょうちん"},
                {"japanese": "光", "english": "light", "reading": "ひかり"}
            ],
            "can_be_taken": True,
            "hidden": False
        },
        {
            "id": "fishing_rod",
            "name": "Bamboo Fishing Rod",
            "japanese_name": "竹の釣り竿",
            "description": "A simple but effective fishing rod made from bamboo.",
            "japanese_description": "竹で作られたシンプルだが効果的な釣り竿。",
            "type": "general",
            "location": "river",
            "properties": {
                "use_effect": "You catch a small fish with the rod."
            },
            "vocabulary": [
                {"japanese": "釣り竿", "english": "fishing rod", "reading": "つりざお"},
                {"japanese": "釣る", "english": "to fish", "reading": "つる"}
            ],
            "can_be_taken": True,
            "hidden": False
        },
        {
            "id": "omamori",
            "name": "Protective Charm",
            "japanese_name": "お守り",
            "description": "A small brocade pouch containing prayers for protection and good fortune.",
            "japanese_description": "守護と幸運の祈りが込められた小さな錦の袋。",
            "type": "quest",
            "location": "shrine",
            "properties": {
                "use_effect": "The charm glows softly, filling you with courage."
            },
            "vocabulary": [
                {"japanese": "お守り", "english": "protective charm", "reading": "おまもり"},
                {"japanese": "祈り", "english": "prayer", "reading": "いのり"},
                {"japanese": "幸運", "english": "good fortune", "reading": "こううん"}
            ],
            "can_be_taken": True,
            "hidden": False
        }
    ],
    "vocabulary": [
        {
            "japanese": "冒険",
            "english": "adventure",
            "reading": "ぼうけん",
            "part_of_speech": "noun",
            "example_sentence": "新しい冒険が始まります。",
            "notes": "Used to refer to an exciting or dangerous journey"
        },
        {
            "japanese": "旅人",
            "english": "traveler",
            "reading": "たびびと",
            "part_of_speech": "noun",
            "example_sentence": "彼は遠くから来た旅人です。",
            "notes": "A person who travels, especially to distant places"
        },
        {
            "japanese": "探検",
            "english": "exploration",
            "reading": "たんけん",
            "part_of_speech": "noun",
            "example_sentence": "山の探検は楽しかったです。",
            "notes": "The act of exploring an unfamiliar area"
        },
        {
            "japanese": "道",
            "english": "road, path",
            "reading": "みち",
            "part_of_speech": "noun",
            "example_sentence": "この道は森に続いています。",
            "notes": "Can refer to both literal paths and figurative ones"
        },
        {
            "japanese": "見る",
            "english": "to see, to look",
            "reading": "みる",
            "part_of_speech": "verb",
            "example_sentence": "景色を見てください。",
            "notes": "Basic verb for visual perception"
        },
        {
            "japanese": "行く",
            "english": "to go",
            "reading": "いく",
            "part_of_speech": "verb",
            "example_sentence": "山に行きましょう。",
            "notes": "Basic verb of motion"
        },
        {
            "japanese": "話す",
            "english": "to speak, to talk",
            "reading": "はなす",
            "part_of_speech": "verb",
            "example_sentence": "村人と話しました。",
            "notes": "Used for general conversation"
        },
        {
            "japanese": "取る",
            "english": "to take, to pick up",
            "reading": "とる",
            "part_of_speech": "verb",
            "example_sentence": "地図を取りました。",
            "notes": "Used for acquiring or picking up objects"
        },
        {
            "japanese": "使う",
            "english": "to use",
            "reading": "つかう",
            "part_of_speech": "verb",
            "example_sentence": "コンパスを使いましょう。",
            "notes": "Indicates utilizing an object for its purpose"
        },
        {
            "japanese": "助ける",
            "english": "to help",
            "reading": "たすける",
            "part_of_speech": "verb",
            "example_sentence": "村人を助けなければなりません。",
            "notes": "Used when providing assistance"
        }
    ]
} 