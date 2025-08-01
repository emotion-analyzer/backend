from datetime import datetime

from analyzer.core.schemas import BatchResponse

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

valid_batch_prompt_1 = {
    "posts": [valid_post_1, valid_post_2]
}

analysis_post_1 = BatchResponse(link=valid_post_1["link"],
                                text=valid_post_1["text"],
                                dominant_emotion= "triste")

analysis_post_2 = BatchResponse(link=valid_post_1["link"],
                                text=valid_post_1["text"],
                                dominant_emotion= "harto")

