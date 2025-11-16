"""
Example datasets and data loading utilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_example(dataset_name: str) -> pd.DataFrame:
    """
    Load an example dataset.

    Parameters
    ----------
    dataset_name : str
        Name of example dataset:
        - 'dichotomous': Example with binary outcomes
        - 'continuous': Example with continuous outcomes
        - 'sparse': Example with rare events

    Returns
    -------
    pd.DataFrame
        Example dataset
    """
    if dataset_name == 'dichotomous':
        return _example_dichotomous()
    elif dataset_name == 'continuous':
        return _example_continuous()
    elif dataset_name == 'sparse':
        return _example_sparse()
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def _example_dichotomous() -> pd.DataFrame:
    """
    Example dataset with dichotomous outcomes.

    Based on simulated data for a hypothetical intervention
    reducing mortality risk.
    """
    np.random.seed(42)

    data = {
        'study_id': [f'Study_{i:02d}' for i in range(1, 21)],
        'year': list(range(2005, 2025)),
        'events_treatment': [12, 15, 8, 22, 18, 14, 9, 11, 16, 13,
                           10, 19, 7, 14, 12, 15, 11, 13, 9, 10],
        'n_treatment': [100, 120, 80, 150, 140, 110, 90, 105, 130, 115,
                       95, 145, 85, 120, 100, 125, 105, 110, 92, 98],
        'events_control': [18, 22, 15, 32, 28, 21, 16, 19, 25, 20,
                         17, 29, 14, 23, 19, 24, 18, 21, 15, 17],
        'n_control': [100, 120, 80, 150, 140, 110, 90, 105, 130, 115,
                     95, 145, 85, 120, 100, 125, 105, 110, 92, 98],
    }

    return pd.DataFrame(data)


def _example_continuous() -> pd.DataFrame:
    """
    Example dataset with continuous outcomes.

    Based on simulated data for a hypothetical intervention
    reducing blood pressure.
    """
    np.random.seed(42)

    data = {
        'study_id': [f'Study_{i:02d}' for i in range(1, 16)],
        'year': list(range(2010, 2025)),
        'mean_treatment': [125.3, 128.1, 122.5, 126.8, 123.9, 127.2, 124.6,
                         125.8, 123.2, 126.5, 124.1, 125.5, 123.8, 126.0, 124.3],
        'sd_treatment': [12.5, 13.2, 11.8, 12.9, 12.1, 13.0, 12.3,
                        12.7, 11.9, 12.8, 12.2, 12.6, 12.0, 12.5, 12.4],
        'n_treatment': [50, 60, 45, 55, 52, 58, 48, 53, 49, 56, 51, 54, 47, 52, 50],
        'mean_control': [132.5, 135.2, 130.8, 134.1, 131.5, 133.8, 132.0,
                        133.2, 131.0, 134.5, 131.8, 133.5, 130.9, 133.0, 131.5],
        'sd_control': [13.0, 13.8, 12.5, 13.5, 12.8, 13.6, 13.1,
                      13.3, 12.6, 13.7, 13.0, 13.4, 12.7, 13.2, 13.0],
        'n_control': [50, 60, 45, 55, 52, 58, 48, 53, 49, 56, 51, 54, 47, 52, 50],
    }

    return pd.DataFrame(data)


def _example_sparse() -> pd.DataFrame:
    """
    Example dataset with sparse data (rare events).

    Based on simulated data for a rare adverse event.
    """
    np.random.seed(42)

    data = {
        'study_id': [f'Study_{i:02d}' for i in range(1, 16)],
        'year': list(range(2010, 2025)),
        'events_treatment': [0, 1, 0, 2, 1, 0, 1, 0, 1, 2, 0, 1, 0, 1, 0],
        'n_treatment': [200, 250, 180, 300, 220, 190, 210, 185, 240, 280,
                       195, 260, 175, 230, 200],
        'events_control': [2, 3, 1, 5, 3, 2, 3, 1, 4, 5, 2, 4, 1, 3, 2],
        'n_control': [200, 250, 180, 300, 220, 190, 210, 185, 240, 280,
                     195, 260, 175, 230, 200],
    }

    return pd.DataFrame(data)
