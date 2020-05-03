import os
from dataclasses import asdict
from html import escape as html_escape
from typing import Tuple, Optional
from urllib.parse import urljoin

from IPython.display import display, HTML
import numpy as np
import requests
from qiskit import QuantumCircuit

from may4_challenge.api import get_root_url, get_api_auth_url, get_exercise_url
from may4_challenge_common import EX4_REFERENCE_UNITARY, circuit_to_json
from may4_challenge_common.ex4 import check_and_score_circuit


_exercise_url = '/challenges/4anniversary?exercise=4'


def get_unitary() -> np.ndarray:
    copy = np.empty_like(EX4_REFERENCE_UNITARY)
    np.copyto(copy, EX4_REFERENCE_UNITARY)
    return copy


def check_circuit(circuit: QuantumCircuit) -> None:
    if type(circuit) is not QuantumCircuit:
        raise ValueError(
            f'parameter must be a qiskit.QuantumCircuit instance, found a {type(circuit)}')

    data = _validate(circuit)

    is_valid = data.get('is_valid', False)
    delta = data.get('delta', None)
    complexity = data.get('complexity', None)
    score = data.get('score', None)
    cause = data.get('cause', None)

    print('Circuit stats:')
    if delta:
        print(f'||U-V||_2 = {delta}')
        print('(U is the reference unitary, V is yours, and the global '
              'phase has been removed from both of them).')
    if complexity:
        print(f'Cost is {complexity}')
    else:
        print(f'Unable to compute cost: double check your circuit is made '
              'of `u3` and `cx` gates only.')
    print()

    if is_valid:
        print('Great! Your circuit meets all the constrains.')
        print(f'Your score is {score}. The lower, the better!')
        print('Feel free to submit your answer and remember you '
              'can re-submit a new circuit at any time!')
    else:
        print(f'Something is not right with your circuit: {cause}')


def _validate(circuit: QuantumCircuit) -> dict:
    try:
        is_valid, details = check_and_score_circuit(circuit)
        json = {'is_valid': is_valid}
        json.update({k: v for k, v in asdict(details).items() if v is not None})
        return json

    except Exception as err:
        return {
            'is_valid': False,
            'cause': f'{err}'
        }


def submit_circuit(circuit: QuantumCircuit) -> None:
    baseurl = get_api_auth_url()
    endpoint = urljoin(baseurl, './challenges/answers')
    payload = circuit_to_json(circuit)

    access_token = _get_access_token()
    response = requests.post(endpoint, json={
        'questionNumber': 4,
        'answer': payload
    }, params={'access_token': access_token})

    response.raise_for_status()
    data = response.json()
    _display_submit_result(data)


def _get_access_token() -> str:
    baseurl = get_api_auth_url()
    endpoint = urljoin(baseurl, './users/loginWithToken')
    iqx_api_key = os.getenv('QXToken', None)
    if iqx_api_key is None:
        raise ValueError('missing IQX API key. Set the environment variable '
                         '`QXToken` with a valid API key.')

    response = requests.post(endpoint, json={'apiToken': iqx_api_key})

    response.raise_for_status()
    return response.json()['id']


def _display_submit_result(data: dict) -> None:
    if data['valid']:
        display(HTML(f"""
        <div style="border: 2px solid black; padding: 2rem;">
            <p>
                Success 🎉! Your circuit has been submitted. Return to the
                <a href="{html_escape(get_exercise_url(4))}" target="_blank">
                    IBM Quantum Challenge page
                </a>
                and check your score and ranking.
            </p>
            <p>
                Remember that you can submit a circuit as many times as you
                want.
            </p>
        </div>"""))
    else:
        display(HTML(f"""
            <p style="border: 2px solid black; padding: 2rem;">
                Oops 😕! Your circuit does not seem valid. Use
                <code>check_circuit()</code> to validate your circuit before
                submitting.
            </p>
        """))
