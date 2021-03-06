"""Utilities for input validation"""
# License : Apache 2.0

import numbers

import numpy as np

available_metrics = {'bottleneck': [('delta', numbers.Number, (0., 1.))],
                     'wasserstein': [('p', int, (1, np.inf)),
                                     ('delta', numbers.Number, (1e-16, 1.))],
                     'betti': [('p', numbers.Number, (1, np.inf)),
                               ('n_values', int, (1, np.inf))],
                     'landscape': [('p', numbers.Number, (1, np.inf)),
                                   ('n_values', int, (1, np.inf)),
                                   ('n_layers', int, (1, np.inf))],
                     'heat': [('order', numbers.Number, (1, np.inf)),
                              ('n_values', int, (1, np.inf)),
                              ('sigma', numbers.Number, (0., np.inf))]}

available_metric_params = list(set(
    [param for param_list in available_metrics.values()
     for (param, param_type, param_range) in param_list]))


def check_diagram(X):
    """Input validation on a diagram
    """
    if len(X.shape) != 3:
        raise ValueError("X should be a 3d np.array: X.shape"
                         " = {}".format(X.shape))
    if X.shape[2] != 3:
        raise ValueError("X should be a 3d np.array with a 3rd dimension of"
                         " 3 components: X.shape[2] = {}".format(X.shape[2]))

    homology_dimensions = sorted(list(set(X[0, :, 2])))
    for dim in homology_dimensions:
        if dim == np.inf:
            if len(homology_dimensions) != 1:
                raise ValueError("np.inf is a valid homology dimension for a "
                                 "stacked diagram but it should be the only "
                                 "one: homology_dimensions "
                                 "= {}".format(homology_dimensions))
        else:
            if dim != int(dim):
                raise ValueError("All homology dimensions should be"
                                 " integer valued: {} can't be casted"
                                 " to an int of the same value.".format(dim))
            if dim != np.abs(dim):
                raise ValueError("All homology dimensions should be"
                                 " integer valued: {} can't be casted"
                                 " to an int of the same value.".format(dim))

    n_points_above_diag = np.sum(X[:, :, 1] >= X[:, :, 0])
    n_points_global = X.shape[0] * X.shape[1]
    if n_points_above_diag != n_points_global:
        raise ValueError("All points of all n_samples persistent diagrams "
                         "should be above the diagonal, X[:,:,1] > =X[:,:,0]."
                         f" {n_points_global - n_points_above_diag} points in "
                         "all n_samples diagrams are under the diagonal.")
    return X

# Chech graph input matrices
''' This function check the input adjacency matrices values: in particular check that the X shape
has three dimension and that every NxN adjancency matrix is a square matrix, every diagonal
element of every matrix is zero and every matrix is symmetric.
'''
def check_graph(X):
    if len(X.shape) != 3:
        raise ValueError("Graph structure dimension error: {}. "
                         "Graph structure dimension must be equal "
                         "to 3.".format(len(X.shape)))
    if X.shape[1] != X.shape[2]:
        raise TypeError("Matrix is not square")
    if np.sum(np.diagonal(X, axis1=1, axis2=2)) != 0:
        raise ValueError("At least one matrix diagonal element is not 0")
    if not np.allclose(X, np.transpose(X, (0, 2, 1))):
        raise ValueError("Matrix is not symmetric")
    if np.sum(X < 0) > 0:
        raise ValueError("At least one matrix element is smaller than 0")
    return X


# Check the type and range of numerical parameters
def validate_params(parameters, references):
    for key in references.keys():
        if not isinstance(parameters[key], references[key][0]):
            raise TypeError("Parameter {} is of type {}"
                            " while it should be of type {}"
                            "".format(key, type(parameters[key]),
                                      references[key][0]))
        if len(references[key]) == 1:
            continue
        if references[key][0] == list:
            for parameter in parameters[key]:
                if not isinstance(parameter, references[key][1][0]):
                    raise TypeError("Parameter {} is a list of {}"
                                    " but contains an element of type {}"
                                    "".format(key, type(parameters[key]),
                                              references[key][0]))
                if isinstance(references[key][1], tuple):
                    if (parameter < references[key][1][1][0] or
                            parameter > references[key][1][1][1]):
                        raise ValueError("Parameter {} is a list containing {}"
                                         "which should be in the range ({},{})"
                                         "".format(key, parameter,
                                                   references[key][1][1][0],
                                                   references[key][1][1][1]))
            break
        if isinstance(references[key][1], tuple):
            if (parameters[key] < references[key][1][0] or
                    parameters[key] > references[key][1][1]):
                raise ValueError("Parameter {} is {}, while it"
                                 " should be in the range ({},{})"
                                 "".format(key, parameters[key],
                                           references[key][1][0],
                                           references[key][1][1]))
        if isinstance(references[key][1], list):
            if parameters[key] not in references[key][1]:
                raise ValueError("Parameter {} is {}, while it"
                                 " should be one of the following {}"
                                 "".format(key, parameters[key],
                                           references[key][1]))


def validate_metric_params(metric, metric_params):
    if metric not in available_metrics.keys():
        raise ValueError("No metric called {}."
                         " Available metrics are {}."
                         "".format(metric,
                                   list(available_metrics.keys())))

    for (param, param_type, param_values) in available_metrics[metric]:
        if param in metric_params.keys():
            input_param = metric_params[param]
            if not isinstance(input_param, param_type):
                raise TypeError("{} in params_metric is of type {}"
                                " but must be an {}."
                                "".format(param, type(input_param),
                                          param_type))

            if input_param < param_values[0] or input_param > param_values[1]:
                raise ValueError("{} in param_metric should be between {} "
                                 "and {} but has been set to {}."
                                 "".format(param, param_values[0],
                                           param_values[1], input_param))

    for param in metric_params.keys():
        if param not in available_metric_params:
            raise ValueError("{} in param_metric is not an available"
                             " parameter. Available metric_params."
                             " are {}".format(param,
                                              available_metric_params))
