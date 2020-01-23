import numpy as np


def get_median(list_input):
    assert isinstance(list_input, list)
    return -1 if not len(list_input) else np.median(list_input)


def get_std(list_input):
    assert isinstance(list_input, list)
    return -1 if not len(list_input) else np.std(list_input)


def de_noise(list_input):
    assert isinstance(list_input, list)
    median = np.median(list_input)
    # b = 1.4826
    b = 0.5
    mad = b * np.median(np.abs(list_input - median))
    lower_limit = median - (3 * mad)
    upper_limit = median + (3 * mad)

    list_return = list_input.copy()

    for element in list_input:
        if not lower_limit <= element <= upper_limit:
            # print(' -Removed.')
            list_return.remove(element)
    return list_return
