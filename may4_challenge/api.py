import os
from urllib.parse import urlencode
from typing import Optional
from sys import stderr


_root_url: Optional[str] = None
_exercises_url: Optional[str] = None
_api_auth_url: Optional[str] = None


def get_root_url() -> str:
    global _root_url
    if not _root_url:
        url = os.getenv('MAY4_CHALLENGE_VALIDATION_ENDPOINT')
        if not url:
            print(f'Missing environment variable MAY4_CHALLENGE_VALIDATION_ENDPOINT. '
                  'Set it with the URL to the root of the validation server.', file=stderr)

            url = 'https://eu-gb.functions.cloud.ibm.com/api/v1/web/salvador.de.la.puente.gonzalez%40ibm.com_dev/default/may4_challenge'  # noqa E501
            print(file=stderr)
            print(f'Using staging server at {url}', file=stderr)

        _root_url = _normalize_final_slash(url)

    return _root_url


def get_api_auth_url() -> str:
    global _api_auth_url
    if not _api_auth_url:
        url = os.getenv('MAY4_CHALLENGE_API_AUTH_ENDPOINT')
        if not url:
            print(f'Missing environment variable MAY4_CHALLENGE_API_AUTH_ENDPOINT. '
                  'Set it with the URL to the root of the api-auth API.', file=stderr)

            url = 'https://auth-dev.quantum-computing.ibm.com/api'
            print(file=stderr)
            print(f'Using staging server at {url}', file=stderr)

        _api_auth_url = _normalize_final_slash(url)

    return _api_auth_url


def get_exercise_url(exercise_id: Optional[int] = None, answer: Optional[str] = None) -> str:
    global _exercises_url
    if not _exercises_url:
        url = os.getenv('MAY4_CHALLENGE_LANDING_PAGE')
        if not url:
            print(f'Missing environment variable MAY4_CHALLENGE_LANDING_PAGE. '
                  'Set it with the URL to the challenge landing page.', file=stderr)

            url = 'https://iqx-web-pr-feature-may-4.mybluemix.net/challenges/4anniversary'
            print(file=stderr)
            print(f'Using testing server at {url}', file=stderr)

        _exercises_url = _normalize_final_slash(url)

    params = {k: v for k, v in [('exercise', exercise_id), ('answer', answer)] if v is not None}
    query_string = f'?{urlencode(params)}' if params else ''
    return f'{_exercises_url}{query_string}'


def _normalize_final_slash(url: str) -> str:
    if url[-1] != '/':
        url += '/'

    return url
