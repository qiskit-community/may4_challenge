import os
import pickle
import json
from urllib.parse import urljoin
from typing import Tuple
from html import escape as html_escape

import requests
from qiskit import QuantumCircuit
from qiskit.qobj import Qobj
from qiskit.assembler import disassemble
from IPython.display import display, HTML

from may4_challenge_common import dict_to_circuit
from may4_challenge.api import get_root_url, get_exercise_url


def show_message(message: str) -> None:
    display(HTML(f"""
    <p style="border: 2px solid black; padding: 2rem;">
        Congratulations 🎉! Submit the following text
        <samp
            style="font-family: monospace; background-color: #eee;"
        >{html_escape(message)}</samp>
        on the
        <a href="{html_escape(get_exercise_url(exercise_id=3, answer=message))}" target="_blank">
            IBM Quantum Challenge page
        </a>
        to see if you are correct.
    </p>
    """))


def initialize_circuit() -> QuantumCircuit:
    circuit_path = os.path.join(os.path.dirname(__file__), 'ex3_circuit.bin')
    if not os.path.exists(circuit_path):
        raise Exception(f'Circuit for exercise 3 not found at {circuit_path}')

    with open(circuit_path, mode='tr') as file_:
        data = json.load(file_)
    circuit = dict_to_circuit(data)

    return circuit


def alice_prepare_qubit(qubit_index: int) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)

    x_indices = [0, 6, 11, 12, 13, 18, 19, 20, 22, 26, 27, 28, 31, 32, 33, 34, 37, 39, 44, 45, 51, 52, 55, 59, 61, 62, 63, 66, 68, 72, 73, 77, 79, 81, 87, 90, 93, 99]  # noqa
    if qubit_index in x_indices:
        qc.x(0)

    h_indices = [0, 11, 15, 16, 17, 18, 19, 20, 21, 24, 25, 27, 28, 31, 33, 37, 38, 39, 40, 41, 43, 46, 47, 49, 50, 51, 52, 53, 54, 58, 59, 65, 66, 72, 75, 76, 80, 81, 82, 85, 86, 87, 89, 92, 97, 98]  # noqa
    if qubit_index in h_indices:
        qc.h(0)

    return qc


def check_bits(bits: str) -> None:
    is_valid, cause = _do_check_bits(0, bits)

    if is_valid:
        print('So far, so good 🎉! You got the right bits!')
    else:
        print('Oops 😕! Not the right bits.')
        if cause is not None:
            print(f'A possible cause is: {cause}')


def check_key(key: str) -> None:
    is_valid, cause = _do_check_bits(1, key)

    if is_valid:
        print('So far, so good 🎉! You got the right key!')
    else:
        print('Oops 😕! Not the right bits.')
        if cause is not None:
            print(f'A possible cause is: {cause}')


def check_decrypted(decrypted: str) -> None:
    is_valid, cause = _do_check_bits(2, decrypted)

    if is_valid:
        print('So far, so good 🎉! You decrypted the message!')
    else:
        print('Oops 😕! Not the right bits.')
        if cause is not None:
            print(f'A possible cause is: {cause}')


def _do_check_bits(kind: int, bits: str) -> Tuple[bool, str]:
    root_url = get_root_url()
    endpoint = urljoin(root_url, './ex3/validate-bits')
    response = requests.post(endpoint, json={
        'kind': kind,
        'bits': bits
    })

    response.raise_for_status()
    data = response.json()

    is_valid = data['is_valid']
    cause = data['cause'] if 'cause' in data else None
    return is_valid, cause
