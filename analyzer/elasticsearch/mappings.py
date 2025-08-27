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
        "source": {"type": "text"},
        "link": {"type": "text"},
        "text": {"type": "text"},
        "timestamp": {"type": "date"},
        "model": {"type": "text"},
        "affective_states": {
            "type": "object",
            "dynamic": True
        }
    }
}
