from typing import Sequence

import numpy as np


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine of the angle between two vectors: 1 = same direction, 0 = unrelated, -1 = opposite.

    A zero vector has no direction, so its similarity to anything is 0.
    """
    va = np.asarray(a, dtype=float)
    vb = np.asarray(b, dtype=float)
    if va.shape != vb.shape:
        raise ValueError(f"vectors have different lengths ({va.shape[0]} vs {vb.shape[0]})")
    norm = np.linalg.norm(va) * np.linalg.norm(vb)
    if norm == 0:
        return 0.0
    return float(np.clip(np.dot(va, vb) / norm, -1.0, 1.0))
