from analyzer.core.schemas import AnalyzePromptResponse

invalid_prompt_1 = {
    "input": "Este prompt es invalido",
}

invalid_batch_prompt_1 = {
    "inputs": [
        "Este prompt es invalido",
        "Este prompt tambien es invalido",
    ]
}

valid_prompt_1 = {
    "text": "Este prompt es valido",
}

valid_batch_prompt_1 = {
    "texts": [
        "Este prompt es valido",
        "Este prompt tambien es valido",
    ]
}

analysis_response = AnalyzePromptResponse(dominant_emotion='emotion1',
                                          emotions={'emotion1': 0.6,
                                                    'emotion2': 0.4})
