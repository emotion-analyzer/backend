from prometheus_client import Counter, Histogram

emotional_analysis_duration = Histogram(
    'emotional_analysis_duration_seconds',
    'Emotional analysis duration',
    ['model']
)

elasticsearch_operation_duration = Histogram(
    'elasticsearch_operation_duration_seconds',
    'Elasticsearch operation duration',
    ['operation']
)

requests = Counter(
    'requests_total',
    'Total amount of requests',
    ['model']
)

score = Counter(
    'score',
    'Main (first) score for each prediction',
    ['model']
)
