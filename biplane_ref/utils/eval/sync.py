# name: sync.py


import numpy as np
from scipy import signal
from copy import deepcopy


def find_lag(signal1, signal2):
    ''' Find the lag between two signals 
    
    Args:
        signal1 (np.array): first signal
        signal2 (np.array): second signal
        
        Returns:
            lag (int): lag between the two signals
    '''

    corr = np.correlate(signal1, signal2, mode = 'full')
    lags = signal.correlation_lags(len(signal1), len(signal2))
    # lags = np.arange(-len(signal2)+1, len(signal1))
    lag  = lags[np.argmax(abs(corr))]
    # lag = lags[np.argmax(corr)]

    return lag


def sync_data(ja, lag, ja_length):
    ''' Sync the data based on the lag

    Args:
        ja (dict): joint angles
        lag (int): lag between the two signals
        ja_length (int): length of the synced joint angles
        
    Returns:
        ja (dict): synced joint angles
    '''

    synced_ja = {}
    for joint in ja.keys():
        synced_ja[joint] = ja[joint][lag:lag + ja_length]

    return synced_ja


def apply_sync(ja1, ja2, lag):
    ''' Sync the data based on the lag

    Args:
        ja1 (dict): joint angles from source 1
        ja2 (dict): joint angles from source 2
        lag (int): lag between the two signals

    Returns:
        ja1 (dict): synced joint angles from source 1
        ja2 (dict): synced joint angles from source 2
    '''

    ja1_new = deepcopy(ja1)
    ja2_new = deepcopy(ja2)
    if lag >= 0:
        ja_length = len(ja2[list(ja2.keys())[0]])
        ja1_new   = sync_data(ja1, lag, ja_length)

    elif lag < 0:
        ja_length = len(ja1[list(ja1.keys())[0]])
        ja2_new   = sync_data(ja2, -lag, ja_length)

    return ja1_new, ja2_new


def find_best_match(long_sig, short_sig, nan_flag = False):
    """
    Find where `short_sig` best matches inside `long_sig` using z-normalized cross-correlation.
    Returns (start_idx, ncc_max, ncc_series).

    long_sig: 1D array-like, length N
    short_sig: 1D array-like, length M (M <= N)
    """
    
    x = np.asarray(long_sig, dtype=float)
    q = np.asarray(short_sig, dtype=float)

    if nan_flag:
        q = q[~np.isnan(q)]  # remove NaN values from short_sig
        
    N, M = x.size, q.size
    if M > N:
        raise ValueError("short_sig must not be longer than long_sig")

    # Precompute stats for short signal
    q_mean = q.mean()
    q_std = q.std()
    # print(x)
    if q_std == 0:
        raise ValueError("short_sig has zero variance")
    qz = q - q_mean
    sum_q = q.sum()

    # Rolling sums for all length-M windows of x (for per-window mean/std)
    csum = np.cumsum(np.r_[0.0, x])               # length N+1
    csum2 = np.cumsum(np.r_[0.0, x*x])            # length N+1
    win_sum  = csum[M:]  - csum[:-M]              # length N-M+1
    win_sum2 = csum2[M:] - csum2[:-M]             # length N-M+1
    win_mean = win_sum / M
    # unbiased vs population std isn't important for normalization; use population here
    win_var = np.maximum(win_sum2 / M - win_mean**2, 0.0)
    win_std = np.sqrt(win_var)
    # Guard against zero-variance windows
    valid = win_std > 0

    # Cross term: sum over k of x[i+k]*q[k] for every i (sliding dot product).
    # Use numpy.correlate in 'valid' mode for efficiency.
    # This computes sum_k x[i+k]*q[k] (no reversal), exactly what we need.
    cross = np.correlate(x, q, mode='valid')  # length N-M+1

    # Convert to *normalized* cross-correlation (per-window z-normalization)
    # NCC(i) = (cross(i) - M*win_mean(i)*q_mean) / (M * win_std(i) * q_std)
    ncc = np.full_like(cross, fill_value=np.nan, dtype=float)
    numerator = cross - M * win_mean * q_mean
    denom = (M * win_std * q_std)
    ncc[valid] = numerator[valid] / denom[valid]
    # print(ncc)

    # Best match
    best_idx = int(np.nanargmax(ncc))
    best_score = float(ncc[best_idx])

    # return best_idx, best_score, ncc
    return best_idx





