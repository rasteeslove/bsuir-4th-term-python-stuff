"""
This module contains base methods for iteratively solving systems of
linear equations.  So called 'simple iterations method' and Seidel
method both override the 'solve' method of this module.

The science behind all that follows is to be found here:
https://math.semestr.ru/optim/iter.php
"""


import math
import numpy as np

import system_transform as st


MAX_ITERATIONS_COUNT = 1_000_000

    
def metric_one_coefficient(B):
    B = abs(B)
    row_sums = np.zeros(len(B))

    for i in range(len(B)):
        for j in range(len(B)):
            row_sums[i] += B[i, j]

    return np.amax(row_sums)

def metric_two_coefficient(B):
    B = abs(B)
    col_sums = np.zeros(len(B))

    for j in range(len(B)):
        for i in range(len(B)):
            col_sums += B[i, j]

    return np.amax(col_sums)

def metric_three_coefficient(B):
    squares_sum = 0

    for i in range(len(B)):
        for j in range(len(B)):
            squares_sum += B[i, j]**2

    return squares_sum


def _metric_one_distance(x, y):
    return np.amax(abs(x - y))

def _metric_two_distance(x, y):
    return np.sum(abs(x - y))

def _metric_three_distance(x, y):
    return math.sqrt(np.sum((x-y) ** 2))


def _choose_distance_metric(B):
    """
    Return either [the alpha coefficient and the distance-measuring
    method depending on the chosen metric] or [None if the criteria
    of convergence is not met].
    """
    alpha = metric_one_coefficient(B)
    if alpha < 1:
        return alpha, _metric_one_distance

    alpha = metric_two_coefficient(B)
    if alpha < 1:
        return alpha, _metric_two_distance

    alpha = metric_three_coefficient(B)
    if alpha < 1:
        return alpha, _metric_three_distance

    return None


def check_convergence(A, b):
    """
    Return True if the criteria of convergence is met for the
    A matrix.
    """
    B, _ = st.system_transform(A, b)
    return _choose_distance_metric(B) is not None


def _estimate_error(alpha, first_distance, last_distance, iter_num):
    """
    Return the estimated error for the most recent iteration
    (last_distance).
    """
    estimation_one = (alpha**iter_num / (1-alpha)) * first_distance
    estimation_two = (alpha / (1-alpha)) * last_distance

    return estimation_one if estimation_one < estimation_two else estimation_two


def solve(A, b, precision, iteration_method):
    """
    Return the x-vector solution to the A*x=b equation with error
    within the precision argument value.  For iterating requires
    some iteration method.
    """
    B, c = st.system_transform(A, b)
    distance_metric = _choose_distance_metric(B)

    x = np.zeros(len(A))
    y = iteration_method(B, x, c)

    if distance_metric is None:
        print('The convergence is not guaranteed.')
    else:
        alpha = distance_metric[0]
        calculate_distance = distance_metric[1]

        first_distance = calculate_distance(x, y)
        last_distance = calculate_distance(x, y)

    iter_num = 0
    while (((distance_metric is not None
             and _estimate_error(alpha, first_distance, 
                                 last_distance, iter_num) > precision
            ) or (distance_metric is None)
           ) and iter_num < MAX_ITERATIONS_COUNT):
        x = y
        y = iteration_method(B, x, c)

        if distance_metric is not None:
            last_distance = calculate_distance(x, y)

        iter_num += 1

    return y, iter_num
