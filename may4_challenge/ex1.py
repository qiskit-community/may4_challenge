import json
from html import escape as html_escape
from typing import Any, Union, Tuple, Mapping, Optional
from urllib.parse import urljoin

from IPython.display import display, HTML
import qiskit.quantum_info as qi
from qiskit import Aer, execute, QuantumCircuit
import numpy as np
import requests

from may4_challenge.api import get_root_url, get_exercise_url
from may4_challenge.widgets import minicomposer  # type: ignore
from may4_challenge_common import bloch_vec, statevec, vec_in_braket, return_state
from may4_challenge_common import EX1_SUBEXERCISE_COUNT as SUBEXERCISE_COUNT


_scores = [0] * SUBEXERCISE_COUNT
_result_cell: Optional[HTML] = None


def check1(bloch_vector: np.ndarray) -> None:
    check_statevector(1, bloch_vector)


def check2(bloch_vector: np.ndarray) -> None:
    check_statevector(2, bloch_vector)


def check3(bloch_vector: np.ndarray) -> None:
    check_statevector(3, bloch_vector)


def check4(bloch_vector: np.ndarray) -> None:
    check_statevector(4, bloch_vector)


def check5(braket_repr: np.ndarray) -> None:
    check_statevector(5, braket_repr)


def check6(braket_repr: np.ndarray) -> None:
    check_statevector(6, braket_repr)


def check7(braket_repr: np.ndarray) -> None:
    check_statevector(7, braket_repr)


def check8(counts: Mapping[str, int]) -> None:
    check_counts(8, counts)


def check_bloch_vector(subexercise_id: int, bloch_vector: np.ndarray) -> None:
    if type(bloch_vector) not in [np.ndarray, list, tuple]:
        raise ValueError(f'expected a list, tuple or numpy ndarray, got a {type(bloch_vector)}')

    if hasattr(bloch_vector, 'tolist'):
        bloch_vector_as_list_repr = json.dumps(bloch_vector.tolist())
    else:
        bloch_vector_as_list_repr = json.dumps(bloch_vector)

    _check_subexercise(subexercise_id, bloch_vector_as_list_repr)


def check_statevector(subexercise_id: int, statevector: qi.Statevector) -> None:
    if type(statevector) is not qi.Statevector:
        raise ValueError(
            'expected a qiskit.quantum_info.Statevector, '
            f'got a {type(statevector)}')

    list_form = statevector.data.tolist()
    list_of_pairs = list(map(_complex_as_tuple, list_form))
    statevector_as_list_repr = json.dumps(list_of_pairs)

    if subexercise_id == 6:
        _check_subexercise(subexercise_id, statevector_as_list_repr,
                           'Hint: You might want to start by creating the Bell'
                           'state from before and then apply some single-qubit '
                           'gates.')
    else:
        _check_subexercise(subexercise_id, statevector_as_list_repr)


def check_braket_vector(subexercise_id: int, braket_repr: str) -> None:
    if type(braket_repr) is not str:
        raise ValueError(f'expected a string, got a {type(braket_repr)}')

    _check_subexercise(subexercise_id, braket_repr.strip())


def check_counts(subexercise_id: int, counts: Mapping[str, int]) -> None:
    if not isinstance(counts, Mapping):
        raise ValueError(f'expected a mapping (such as a dict), got a {type(counts)}')

    counts_as_dics_repr = json.dumps({**counts})
    _check_subexercise(subexercise_id, counts_as_dics_repr)


def _complex_as_tuple(v: Union[float, int, complex]) -> Tuple[float, float]:
    c = complex(v)
    return c.real, c.imag


def _check_subexercise(subexercise_id: int, answer: Any, hint: str = '') -> None:
    root_url = get_root_url()
    endpoint = urljoin(root_url, './ex1/validate-subexercise')
    response = requests.post(endpoint, json={
        'subexercise_id': subexercise_id,
        'answer': answer
    })

    response.raise_for_status()
    data = response.json()
    is_valid = data['is_valid']

    result_msg = 'Correct 🎉! Well done!' if is_valid else 'Oops 😕! Incorrect, try again!'
    print(result_msg)
    if not is_valid and hint:
        print(hint)

    _scores[subexercise_id-1] = data['score'] if is_valid else 0
    score_msg = f'Your progress: {_count_done()}/8'
    print(score_msg)
    if _is_victory():
        _display_victory(repr(_scores))


def _is_victory() -> bool:
    return SUBEXERCISE_COUNT - _count_done() == 0


def _display_victory(result: str) -> None:
    display(HTML(f"""
    <p style="border: 2px solid black; padding: 2rem;">
        Congratulations 🎉! Submit the following text
        <samp
            style="font-family: monospace; background-color: #eee;"
        >{html_escape(result)}</samp>
        on the
        <a href="{html_escape(get_exercise_url(exercise_id=1, answer=result))}" target="_blank">
            IBM Quantum Challenge page
        </a>
        to see if you are correct.
    </p>
    """))


def _count_done() -> int:
    return len([score for score in _scores if score != 0])
