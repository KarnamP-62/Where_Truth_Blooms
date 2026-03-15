import pandas as pd
import json

# Words to filter out
exclude_words = [
    'satyakama', 'satyaloka', 'satyavaha', 'satyayajna',
    'satyayani', 'satyaniyaopanishad', 'tattvamasi',
    'tattvamasyadi', 'yogatattva', 'tat'
]

# Convert to lowercase for comparison
exclude_words_lower = [w.lower() for w in exclude_words]

print("Filtering out words:", exclude_words)
print("=" * 50)

# ==================== 1. REGENERATE data.json (Truth Flowers) ====================
print("\n1. Processing truth_sentences.csv for data.json...")

df = pd.read_csv('/Users/priyankakarnam/Desktop/Data is art/truth_sentences.csv')
print(f"   Original rows: {len(df)}")

# Filter out excluded words
df_filtered = df[~df['words_found'].str.lower().isin(exclude_words_lower)]
print(f"   After filtering: {len(df_filtered)}")
print(f"   Removed: {len(df) - len(df_filtered)} rows")

# Create hierarchical structure
hierarchy = {
    "name": "108 Upanishads",
    "children": []
}

# Group by Veda
for veda in df_filtered['veda'].unique():
    veda_data = df_filtered[df_filtered['veda'] == veda]
    veda_node = {
        "name": veda,
        "children": []
    }

    # Group by Upanishad within each Veda
    for upanishad in veda_data['upanishad'].unique():
        upanishad_data = veda_data[veda_data['upanishad'] == upanishad]
        upanishad_node = {
            "name": upanishad,
            "children": []
        }

        # Add sentences as leaf nodes
        for idx, row in upanishad_data.iterrows():
            sentence = row['sentence']
            if len(sentence) > 100:
                display_sentence = sentence[:100] + "..."
            else:
                display_sentence = sentence

            sentence_node = {
                "name": display_sentence,
                "full_sentence": sentence,
                "words_found": row['words_found'],
                "size": 1
            }
            upanishad_node["children"].append(sentence_node)

        upanishad_node["sentence_count"] = len(upanishad_node["children"])
        veda_node["children"].append(upanishad_node)

    veda_node["upanishad_count"] = len(veda_node["children"])
    veda_node["sentence_count"] = len(veda_data)
    hierarchy["children"].append(veda_node)

# Save data.json
with open('/Users/priyankakarnam/Desktop/Data is art/visualization/data.json', 'w') as f:
    json.dump(hierarchy, f, indent=2)

print("   Saved: data.json")

# ==================== 2. REGENERATE emotions_data.json ====================
print("\n2. Processing emotion_analysis.csv for emotions_data.json...")

df_emotions = pd.read_csv('/Users/priyankakarnam/Desktop/Data is art/emotion_analysis.csv')
print(f"   Original rows: {len(df_emotions)}")

# Filter out excluded words
df_emotions_filtered = df_emotions[~df_emotions['word'].str.lower().isin(exclude_words_lower)]
print(f"   After filtering: {len(df_emotions_filtered)}")
print(f"   Removed: {len(df_emotions) - len(df_emotions_filtered)} rows")

# Load the final emotion classification for scores
df_final_emotion = pd.read_csv('/Users/priyankakarnam/Desktop/Data is art/final_emotion_classification.csv')
df_final_emotion_filtered = df_final_emotion[~df_final_emotion['truth_word'].str.lower().isin(exclude_words_lower)]

# Create emotion hierarchy
emotion_categories = {
    "Connection": ["reverence", "unity", "devotion"],
    "Spiritual": ["bliss", "transcendence", "liberation"],
    "Contemplative": ["peace", "serenity", "detachment"],
    "Knowledge": ["understanding", "wisdom", "enlightenment", "wonder", "awe"],
    "Challenge": ["confusion", "fear", "determination", "longing"]
}

emotions_hierarchy = {
    "name": "Emotions",
    "children": []
}

for category, emotions in emotion_categories.items():
    category_node = {
        "name": category,
        "children": [],
        "count": 0
    }

    for emotion in emotions:
        emotion_node = {
            "name": emotion,
            "count": 0,
            "sentences": []
        }

        # Find sentences with this emotion (check emotion_1 column)
        for idx, row in df_final_emotion_filtered.iterrows():
            if pd.notna(row['emotion_1']) and emotion.lower() in row['emotion_1'].lower():
                emotion_node["sentences"].append({
                    "text": row['sentence'][:150] + "..." if len(row['sentence']) > 150 else row['sentence'],
                    "veda": row['veda'],
                    "score": row['score_1'] if pd.notna(row['score_1']) else 0.5
                })
                emotion_node["count"] += 1

        if emotion_node["count"] > 0:
            category_node["children"].append(emotion_node)
            category_node["count"] += emotion_node["count"]

    if category_node["count"] > 0:
        emotions_hierarchy["children"].append(category_node)

# Save emotions_data.json
with open('/Users/priyankakarnam/Desktop/Data is art/visualization/emotions_data.json', 'w') as f:
    json.dump(emotions_hierarchy, f, indent=2)

print("   Saved: emotions_data.json")

# ==================== 3. REGENERATE context_data.json ====================
print("\n3. Processing philosophical context for context_data.json...")

df_context = pd.read_csv('/Users/priyankakarnam/Desktop/Data is art/final_sbert_philosophical_context.csv')
print(f"   Original rows: {len(df_context)}")

# Filter out excluded words
df_context_filtered = df_context[~df_context['truth_word'].str.lower().isin(exclude_words_lower)]
print(f"   After filtering: {len(df_context_filtered)}")
print(f"   Removed: {len(df_context) - len(df_context_filtered)} rows")

# Create context hierarchy
context_hierarchy = {
    "name": "Philosophical Contexts",
    "children": []
}

for context in df_context_filtered['philosophical_context'].unique():
    context_data = df_context_filtered[df_context_filtered['philosophical_context'] == context]
    context_node = {
        "name": context,
        "count": len(context_data),
        "sentences": []
    }

    for idx, row in context_data.iterrows():
        context_node["sentences"].append({
            "text": row['sentence'][:150] + "..." if len(row['sentence']) > 150 else row['sentence'],
            "veda": row['veda'],
            "score": row['context_score'] if pd.notna(row['context_score']) else 0.5
        })

    context_hierarchy["children"].append(context_node)

# Save context_data.json
with open('/Users/priyankakarnam/Desktop/Data is art/visualization/context_data.json', 'w') as f:
    json.dump(context_hierarchy, f, indent=2)

print("   Saved: context_data.json")

# ==================== SUMMARY ====================
print("\n" + "=" * 50)
print("SUMMARY:")
print(f"Total Vedas: {len(hierarchy['children'])}")
for veda in hierarchy['children']:
    print(f"  {veda['name']}: {veda['upanishad_count']} Upanishads, {veda['sentence_count']} sentences")

total_sentences = sum(v['sentence_count'] for v in hierarchy['children'])
print(f"\nTotal filtered sentences: {total_sentences}")
print("\nAll JSON files regenerated successfully!")
