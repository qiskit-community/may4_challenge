from base64 import b64decode

from flaskwsk import invoke
from may4_challenge_server.api.server import app


def main(args: dict) -> dict:
    ow_response = invoke(app, args)
    # XXX: flaskwsk does not recognize application/json as a text format
    # so it encodes it as base64 [1]. This undo that conversion.
    # [1] https://github.com/alexmilowski/flask-openwhisk/blob/master/flaskwsk/handle.py#L59
    content_type = ow_response.get('headers', {}).get('Content-Type', 'application/octet-stream')
    if content_type == 'application/json':
        data = b64decode(ow_response['body']).decode('utf-8')
        ow_response['body'] = data

    return ow_response
