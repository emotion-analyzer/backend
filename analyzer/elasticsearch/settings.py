analysis_settings = {
    "number_of_shards": 3,        # Adjust based on expected data volume
    "number_of_replicas": 1,       # 1 replica for redundancy
    "refresh_interval": "30s",     # Balance between speed and visibility
    "analysis": {
        "analyzer": {
            "spanish_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "asciifolding",
                           "spanish_stop", "spanish_stemmer_light"]
            }
        },
        "filter": {
            "spanish_stop": {"type": "stop", "stopwords": "_spanish_"},
            "spanish_stemmer_light": {"type": "stemmer", "language": "light_spanish"}
        }
    }
}
