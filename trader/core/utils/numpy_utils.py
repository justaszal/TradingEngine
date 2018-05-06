import numpy as np


def get(arr, x):
    try:
        return arr[x] if x >= 0 else np.nan
    except Exception:
        return np.nan


def shift(arr, num, fill_value=np.nan):
    arr_len = len(arr)

    if num > 0:
        i = arr_len - 1
        while i >= 0:
            arr[i] = get(arr, i - num)
            i -= 1
    elif num < 0:
        i = 0
        while i < arr_len:
            arr[i] = get(arr, i - num)
            i += 1
