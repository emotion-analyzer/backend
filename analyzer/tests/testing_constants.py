from datetime import datetime

from util.schemas import PostAnalysisResult

invalid_batch_prompt_1 = {
    "inputs": [
        "Este prompt es invalido",
        "Este prompt tambien es invalido",
    ]
}

valid_post_1 = {
            "text": "Este prompt es valido",
            "link": "https://www.validlink.com",
            "timestamp": datetime.now().isoformat(),
}

valid_post_2 = {
            "text": "Este prompt tambien es valido",
            "link": "https://www.validlink2.com",
            "timestamp": datetime.now().isoformat()
}

single_post_prompt = {
    "posts": [valid_post_1]
}

valid_batch_prompt_1 = {
    "posts": [valid_post_1, valid_post_2]
}

post_1_affective_states = {"loco": 0.80, "harto": 0.20}
post_1_dominant_affective_state = next(iter(post_1_affective_states.keys()))

post_2_affective_states = {"triste": 0.75, "cansado": 0.25}
post_2_dominant_affective_state = next(iter(post_2_affective_states.keys()))

analysis_post_1 = PostAnalysisResult(link=valid_post_1["link"],
                                     text=valid_post_1["text"],
                                     affective_states=list(post_1_affective_states.keys()),
                                     dominant_affective_state=post_1_dominant_affective_state)

analysis_post_2 = PostAnalysisResult(link=valid_post_2["link"],
                                     text=valid_post_2["text"],
                                     affective_states=list(post_2_affective_states.keys()),
                                     dominant_affective_state=post_2_dominant_affective_state)
