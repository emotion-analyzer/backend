analysis_mappings = {
    "dynamic": False,
    "dynamic_templates": [
        {
            "affective_states_values": {
                "path_match": "affective_states.*",
                "mapping": {
                    "type": "float"
                }
            }
        }
    ],
    "properties": {
        "affective_states": {"type": "object",
                             "dynamic": True},
        "dominant_affective_state": {"type": "text"}
    }
}

