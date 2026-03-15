import pandas as pd
import json

# Read the truth sentences data
df = pd.read_csv('/Users/priyankakarnam/Desktop/Data is art/truth_sentences.csv')

# Create hierarchical structure
hierarchy = {
    "name": "108 Upanishads",
    "children": []
}

# Group by Veda
for veda in df['veda'].unique():
    veda_data = df[df['veda'] == veda]
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
            # Truncate long sentences for display
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

        # Add sentence count to upanishad name
        upanishad_node["sentence_count"] = len(upanishad_node["children"])
        veda_node["children"].append(upanishad_node)

    # Add upanishad count to veda
    veda_node["upanishad_count"] = len(veda_node["children"])
    veda_node["sentence_count"] = len(veda_data)
    hierarchy["children"].append(veda_node)

# Save as JSON for D3.js
with open('/Users/priyankakarnam/Desktop/Data is art/visualization/data.json', 'w') as f:
    json.dump(hierarchy, f, indent=2)

# Print summary
print("Data processed successfully!")
print(f"\nTotal Vedas: {len(hierarchy['children'])}")
for veda in hierarchy['children']:
    print(f"  {veda['name']}: {veda['upanishad_count']} Upanishads, {veda['sentence_count']} sentences")
