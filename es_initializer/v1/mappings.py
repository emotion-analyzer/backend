"""Version 1 de mapeos.

Fecha: 2026-01-19

Cambios: version inicial.
"""

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
        "source": {"type": "keyword", "eager_global_ordinals": True},
        "language": {"type": "keyword", "eager_global_ordinals": True},
        "link": {"type": "keyword"},
        "text": {"type": "text", "analyzer": "spanish_analyzer"},
        "timestamp": {"type": "date"},
        "model": {"type": "keyword", "eager_global_ordinals": True},
        "version": {"type": "keyword"},
        "affective_states": {"type": "object", "dynamic": True},
        "processing_timestamp": {"type": "date"},
    }
}

