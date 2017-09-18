from channels.routing import route

from apps.core.consumers import ws_connect, ws_receive, ws_disconnect


channel_routing = [
    route('websocket.connect', ws_connect, path=r'^/chat/'),
    route('websocket.receive', ws_receive, path=r'^/chat/'),
    route('websocket.disconnect', ws_disconnect, path=r'^/chat/'),
]
