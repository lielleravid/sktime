# -*- coding: utf-8 -*-
# copyright: sktime developers, BSD-3-Clause License (see LICENSE file)
"""Unit tests for (dunder) composition functionality attached to the base class."""

__author__ = ["fkiraly"]
__all__ = []

from sktime.classification.compose import ClassifierPipeline
from sktime.classification.distance_based import KNeighborsTimeSeriesClassifier
from sktime.transformations.series.exponent import ExponentTransformer
from sktime.utils._testing.estimator_checks import _assert_array_almost_equal
from sktime.utils._testing.panel import _make_classification_y, _make_panel_X


def test_dunder_mul():
    """Test the mul dunder method."""
    RAND_SEED = 42
    y = _make_classification_y(n_instances=10, random_state=RAND_SEED)
    X = _make_panel_X(n_instances=10, n_timepoints=20, random_state=RAND_SEED, y=y)
    X_test = _make_panel_X(n_instances=5, n_timepoints=20, random_state=RAND_SEED)

    t1 = ExponentTransformer(power=4)
    t2 = ExponentTransformer(power=0.25)

    c = KNeighborsTimeSeriesClassifier()
    t12c_1 = t1 * (t2 * c)
    t12c_2 = (t1 * t2) * c
    t12c_3 = t1 * t2 * c

    assert isinstance(t12c_1, ClassifierPipeline)
    assert isinstance(t12c_2, ClassifierPipeline)
    assert isinstance(t12c_3, ClassifierPipeline)

    y_pred = c.fit(X, y).predict(X_test)

    _assert_array_almost_equal(y_pred, t12c_1.fit(X, y).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_2.fit(X, y).predict(X_test))
    _assert_array_almost_equal(y_pred, t12c_3.fit(X, y).predict(X_test))

