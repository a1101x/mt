from refreshtoken.models import RefreshToken


def get_form_errors(form):
    errors = {}
    for key, value in form.errors.items():
        messages = []
        for message in value:
            messages.append(message)
        errors[key] = messages
    return errors


def jwt_response_payload_handler(token, user=None, request=None):
    payload = {'token': token,}
    app = 'mt'

    try:
        refresh_token = user.refresh_tokens.get(app=app).key
    except RefreshToken.DoesNotExist:
        refresh_token = None

    payload['refresh_token'] = refresh_token
    return payload
