import aiocache


def init_cache():
    aiocache.caches.set_config({
        'default': {
            'cache': 'aiocache.SimpleMemoryCache',
            'serializer': {'class': 'aiocache.serializers.JsonSerializer'},
        },
    })
