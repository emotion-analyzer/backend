analysis_settings = {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "refresh_interval": "30s",
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
