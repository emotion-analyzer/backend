from collections import Counter
import json

from query_processor.config import config


def map_to_emotions(affective_states):
    """Maps the result of the emotional analysis to a fixed set of emotions."""
    emotions_dict = []
    if not config.MAPPING.APPLY:
        return {}
    with open (config.MAPPING.FILE) as f:
        emotions = json.load(f)
    for state in affective_states:
        neutral = True
        for key, mapped_list in emotions.items():
            genderless_state = f"{state[:-1]}x"
            if state in mapped_list or genderless_state in mapped_list:
                emotions_dict.append(key)
                neutral = False
                break
        if neutral:
            emotions_dict.append("neutral")
    counter = Counter(emotions_dict)
    mapped_counter = {key: value/sum(counter.values()) for key, value in counter.items()}
    return mapped_counter

def process_affective_states(affective_states):
    """Return normalized summary of affective states and mapped emotions."""
    as_counter = Counter(affective_states)
    as_percentages = {key: value/sum(as_counter.values())
                      for key, value in as_counter.items()}
    return as_percentages, map_to_emotions(affective_states)
