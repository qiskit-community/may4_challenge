"""Contain validations to check if a given circuit approximates the reference
unitary and passes the constrains."""
from typing import Tuple, Optional
from dataclasses import dataclass

import qiskit.quantum_info as qi
from qiskit import QuantumCircuit
import numpy as np

from may4_challenge_common import without_global_phase
from may4_challenge_common import EX4_N as N
from may4_challenge_common import EX4_REFERENCE_UNITARY as REFERENCE_UNITARY

EPSILON = 0.01
COMPLEXITY_THRESHOLD = 1600


@dataclass
class Details:
    delta: Optional[float] = None
    complexity: Optional[int] = None
    score: Optional[int] = None
    cause: Optional[str] = None


def check_and_score_circuit(circuit: QuantumCircuit) -> Tuple[bool, Details]:
    is_close_enough, delta = check_circuit_is_close_enough(circuit, REFERENCE_UNITARY, EPSILON)
    meet_constrains, complexity = check_circuit_uses_cnot_and_u3_gates(circuit)
    if not meet_constrains:
        return False, Details(
            delta=delta,
            cause='the circuit contains something else than `u3` and `cx` gates'
        )

    if not is_close_enough:
        return False, Details(
            delta=delta,
            complexity=complexity,
            cause=f'the circuit differs from the unitary more than {EPSILON}'
        )

    assert(complexity is not None)
    if complexity > COMPLEXITY_THRESHOLD:
        return False, Details(
            delta=delta,
            complexity=complexity,
            cause=f'the cost of the circuit is too high (above {COMPLEXITY_THRESHOLD})'
        )

    score = score_circuit(circuit)
    return True, Details(
        delta=delta,
        complexity=complexity,
        score=score
    )


def score_circuit(circuit: QuantumCircuit) -> int:
    return _complexity(circuit)


def check_circuit_uses_cnot_and_u3_gates(circuit: QuantumCircuit) -> Tuple[bool, Optional[int]]:
    ops = {op for op in circuit.count_ops()}
    if ops != {'cx', 'u3'}:
        return False, None

    return True, _complexity(circuit)


def check_circuit_is_close_enough(circuit: QuantumCircuit,
                                  reference: np.ndarray,
                                  epsilon: float) -> Tuple[bool, float]:
    circuit_unitary = get_unitary(circuit)
    norm_2 = _norm_2(circuit_unitary, reference)
    return norm_2 <= epsilon, norm_2


def get_unitary(circuit: QuantumCircuit) -> np.ndarray:
    V = qi.Operator(circuit).data
    return V


def _norm_2(unitary_a: np.ndarray, unitary_b: np.ndarray) -> float:
    return np.linalg.norm(
        without_global_phase(unitary_b)-without_global_phase(unitary_a), ord=2)


def _complexity(circuit: QuantumCircuit) -> int:
    complexity = 0
    for instr, _, _ in circuit.data:
        if instr.name == 'u3':
            complexity += 1
        elif instr.name == 'cx':
            complexity += 10
        else:
            raise ValueError(f'unexpected instruction {instr}. '
                             'Only u3 or cnot gates can be taken into '
                             'consideration')

    return complexity
