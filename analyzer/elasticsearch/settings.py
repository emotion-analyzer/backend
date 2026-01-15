analysis_settings = {
    "index": {
        "refresh_interval": "30s"
    },
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
