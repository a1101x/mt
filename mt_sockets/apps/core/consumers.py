import json

from channels import Group
from channels.sessions import channel_session


@channel_session
def ws_connect(message):
    """
    Listening for connections on /chat/ endpoints.
    """
    try:
        message.reply_channel.send({'accept': True})
        label = message['path'].split('/')[2]
        Group('chat-' + label, channel_layer=message.channel_layer).add(message.reply_channel)
        message.channel_session['room'] = label
    except (KeyError,):
        pass


@channel_session
def ws_receive(message):
    """
    Listening for messages on /chat/ endpoints.
    """
    try:
        label = message.channel_session['room']
        data = json.loads(message['text'])
    except ValueError:
        return

    if data:
        try:
            Group('chat-' + label, channel_layer=message.channel_layer).send({'text': json.dumps(
                {
                    'text': json.loads(message['text']),
                })
            })
        except (KeyError, ValueError):
            return


@channel_session
def ws_disconnect(message):
    """
    Listening for disconnections on /chat/ endpoints.
    """
    try:
        label = message.channel_session['room']
        Group('chat-' + label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError,):
        return
