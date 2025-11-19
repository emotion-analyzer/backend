import json

from util.schemas import DominantEmotion, PostAnalysisResult

with open("fasttext/mapping.json", encoding="utf-8") as f:
    fixed_mapping = json.load(f)

def map_affective_states_to_emotions(affective_states):
    """Maps an emotional analysis result to a fixed set of emotions."""
    emotions=[]
    mapped_affective_states = []
    if len(affective_states) == 0:
        return DominantEmotion(
        label="neutral",
        score=1.00), []
    total = 0
    for state in affective_states.keys():
        try:
            ekman_emotion = fixed_mapping[state]
            score = round(affective_states[state], 2)
            emotions.append((ekman_emotion, score))
            mapped_affective_states.append({
                "label": state,
                "primary_emotion": ekman_emotion,
                "score": score
            })
            total += score
        except KeyError:
            score = round(affective_states[state], 2)
            total += score
            emotions.append(("neutral", score))
            mapped_affective_states.append({
                "label": state,
                "primary_emotion": "neutral",
                "score": score
            })
    emotion_totals = {}
    for emotion, score in emotions:
        emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
    max_emotion = max(emotion_totals, key=emotion_totals.get)
    max_score = emotion_totals[max_emotion]
    result = max_score / total
    return DominantEmotion(
        label=max_emotion,
        score=result), mapped_affective_states

def map_to_fixed_labels(result_list: list[PostAnalysisResult], emotions: list[str]):
    """Return normalized summary of affective states and mapped emotions."""
    for result in result_list:
        affective_states = result["affective_states"]
        (result["dominant_emotion"],
         result["affective_states"]) = map_affective_states_to_emotions(affective_states)
    if "all" in emotions:
        return result_list
    return [result for result in result_list if
            result["dominant_emotion"].label in emotions]
