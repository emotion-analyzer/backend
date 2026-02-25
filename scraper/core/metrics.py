from prometheus_client import Counter

posts_scraped = Counter(
    'posts_scraped_total',
    'Total posts scraped',
    ['platform', 'language']
)
