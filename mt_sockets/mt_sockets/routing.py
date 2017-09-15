from channels.routing import route


channel_routing = [
    route('http.request', 'apps.core.consumers.http_request_consumer')
]
