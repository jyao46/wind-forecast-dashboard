import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon

def rmse(y_true, y_pred):
    y_true = y_true.to_numpy()
    y_pred = y_pred.to_numpy()

    # normalize values
    y_true = (y_true - np.min(y_true)) / (np.max(y_true) - np.min(y_true))
    y_pred = (y_pred - np.min(y_pred)) / (np.max(y_pred) - np.min(y_pred))
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def cross_correlation(y_true, y_pred):
    return float(np.corrcoef(y_true, y_pred)[0, 1])

def power_curve_similarity(speeds, y_true, y_pred, num_bins=50):
    H_true, _, _ = np.histogram2d(speeds, y_true, bins=num_bins, density=True)
    H_pred, _, _ = np.histogram2d(speeds, y_pred, bins=num_bins, density=True)
    H_true_norm = H_true / np.sum(H_true)
    H_pred_norm = H_pred / np.sum(H_pred)
    js_div = jensenshannon(H_true_norm.flatten(), H_pred_norm.flatten())
    return float(1 - js_div)