from collections import Counter
import json

from util.schemas import PostAnalysisResult

with open("fasttext/mapping.json", encoding="utf-8") as f:
    fixed_mapping = json.load(f)

def map_affective_states_to_emotions(affective_states):
    """Maps an emotional analysis result to a fixed set of emotions."""
    emotions=[]
    if len(affective_states) == 0:
        return ["neutral"]
    for state in affective_states.keys():
        for key, mapped_list in fixed_mapping.items():
            genderless_state = f"{state[:-1]}x"
            if state in mapped_list or genderless_state in mapped_list:
                emotions.append(key)
    counts = Counter(emotions)
    max_count = max(counts.values())
    most_common = [k for k, v in counts.items() if v == max_count]
    return most_common

def map_to_fixed_labels(result_list: list[PostAnalysisResult]):
    """Return normalized summary of affective states and mapped emotions."""
    for result in result_list:
        affective_states = result["affective_states"]
        result["dominant_emotions"] = map_affective_states_to_emotions(affective_states)
