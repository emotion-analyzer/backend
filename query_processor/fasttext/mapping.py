from collections import Counter
import json

from util.schemas import PostAnalysisResult

with open("fasttext/mapping.json", encoding="utf-8") as f:
    fixed_mapping = json.load(f)

def map_affective_states_to_emotions(affective_states):
    """Maps an emotional analysis result to a fixed set of emotions."""
    emotions=[]
    mapped_affective_states = []
    if len(affective_states) == 0:
        return "neutral", []
    for state in affective_states.keys():
        genderless_state = f"{state[:-1]}x"
        mapped = False
        for key, mapped_list in fixed_mapping.items():
            if state in mapped_list or genderless_state in mapped_list:
                emotions.append(key)
                mapped_affective_states.append({
                    "label": state,
                    "primary_emotion": key,
                    "score": round(affective_states[state], 2)
                })
                mapped = True
                break
        if not mapped:
            emotions.append("neutral")
            mapped_affective_states.append({
                "label": state,
                "primary_emotion": "neutral",
                "score": round(affective_states[state], 2)
            })
    counts = Counter(emotions)
    max_count = max(counts.values())
    most_common = [k for k, v in counts.items() if v == max_count]
    return most_common[0], mapped_affective_states

def map_to_fixed_labels(result_list: list[PostAnalysisResult], emotions: list[str]):
    """Return normalized summary of affective states and mapped emotions."""
    for result in result_list:
        affective_states = result["affective_states"]
        (result["dominant_emotion"],
         result["affective_states"]) = map_affective_states_to_emotions(affective_states)
    if "all" in emotions:
        return result_list
    return [result for result in result_list if result["dominant_emotion"] in emotions]
