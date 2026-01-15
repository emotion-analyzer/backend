from prometheus_client import Counter, Histogram

emotional_analysis_duration = Histogram(
    'emotional_analysis_duration_seconds',
    'Emotional analysis duration',
    ['model']
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
