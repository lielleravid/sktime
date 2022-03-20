# -*- coding: utf-8 -*-
"""Unit tests for classifier/regressor input output."""

__author__ = ["mloning", "TonyBagnall", "fkiraly"]


import numpy as np
import pytest
from sklearn import clone

from sktime.classification.tests._expected_outputs import (
    basic_motions_proba,
    unit_test_proba,
)
from sktime.datasets import load_basic_motions, load_unit_test
from sktime.tests.test_all_estimators import BaseFixtureGenerator, QuickTester
from sktime.utils._testing.estimator_checks import _assert_array_almost_equal
from sktime.utils._testing.scenarios_classification import (
    ClassifierFitPredictMultivariate,
)


class ClassifierFixtureGenerator(BaseFixtureGenerator):
    """Fixture generator for classifier tests.

    Fixtures parameterized
    ----------------------
    estimator_class: estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
    estimator_instance: instance of estimator inheriting from BaseObject
        ranges over estimator classes not excluded by EXCLUDE_ESTIMATORS, EXCLUDED_TESTS
        instances are generated by create_test_instance class method
    scenario: instance of TestScenario
        ranges over all scenarios returned by retrieve_scenarios
    """

    # note: this should be separate from TestAllClassifiers
    #   additional fixtures, parameters, etc should be added here
    #   Classifiers should contain the tests only

    estimator_type_filter = "classifier"


class TestAllClassifiers(ClassifierFixtureGenerator, QuickTester):
    """Module level tests for all sktime classifiers."""

    def test_multivariate_input_exception(self, estimator_instance):
        """Test univariate classifiers raise exception on multivariate X."""
        # check if multivariate input raises error for univariate classifiers

        # if handles multivariate, no error is to be raised
        #   that classifier works on multivariate data is tested in test_all_estimators
        if estimator_instance.get_tag("capability:multivariate"):
            return None

        error_msg = "X must be univariate"

        scenario = ClassifierFitPredictMultivariate()

        # check if estimator raises appropriate error message
        with pytest.raises(ValueError, match=error_msg):
            scenario.run(estimator_instance, method_sequence=["fit"])

    def test_classifier_output(self, estimator_instance, scenario):
        """Test classifier outputs the correct data types and values.

        Test predict produces a np.array or pd.Series with only values seen in the train
        data, and that predict_proba probability estimates add up to one.
        """
        n_classes = scenario.get_tag("n_classes")
        X_new = scenario.args["predict"]["X"]
        y_train = scenario.args["fit"]["y"]
        y_pred = scenario.run(estimator_instance, method_sequence=["fit", "predict"])

        # check predict
        assert isinstance(y_pred, np.ndarray)
        assert y_pred.shape == (X_new.shape[0],)
        assert np.all(np.isin(np.unique(y_pred), np.unique(y_train)))

        # check predict proba (all classifiers have predict_proba by default)
        y_proba = scenario.run(estimator_instance, method_sequence=["predict_proba"])
        assert isinstance(y_proba, np.ndarray)
        assert y_proba.shape == (X_new.shape[0], n_classes)
        np.testing.assert_allclose(y_proba.sum(axis=1), 1)

    def test_classifier_on_unit_test_data(self, estimator_class):
        """Test classifier on unit test data."""
        # we only use the first estimator instance for testing
        classname = estimator_class.__name__
        estimator_instance = estimator_class.create_test_instance()

        # retrieve expected predict_proba output, and skip test if not available
        if classname in unit_test_proba.keys():
            expected_probas = unit_test_proba[classname]
        else:
            # skip test if no expected probas are registered
            return None

        # set random seed if possible
        estimator_instance = clone(estimator_instance)
        if "random_seed" in estimator_instance.get_params().keys():
            estimator_instance.set_params(random_state=0)

        # load unit test data
        X_train, y_train = load_unit_test(split="train")
        X_test, _ = load_unit_test(split="test")
        indices = np.random.RandomState(0).choice(len(y_train), 10, replace=False)

        # train classifier and predict probas
        estimator_instance.fit(X_train, y_train)
        y_proba = estimator_instance.predict_proba(X_test.iloc[indices])

        # assert probabilities are the same
        _assert_array_almost_equal(y_proba, expected_probas, decimal=2)

    def test_classifier_on_basic_motions(self, estimator_class):
        """Test classifier on basic motions data."""
        # we only use the first estimator instance for testing
        classname = estimator_class.__name__
        estimator_instance = estimator_class.create_test_instance()

        # retrieve expected predict_proba output, and skip test if not available
        if classname in basic_motions_proba.keys():
            expected_probas = basic_motions_proba[classname]
        else:
            # skip test if no expected probas are registered
            return None

        # set random seed if possible
        estimator_instance = clone(estimator_instance)
        if "random_seed" in estimator_instance.get_params().keys():
            estimator_instance.set_params(random_state=0)

        # load unit test data
        X_train, y_train = load_basic_motions(split="train")
        X_test, _ = load_basic_motions(split="test")
        indices = np.random.RandomState(4).choice(len(y_train), 10, replace=False)

        # train classifier and predict probas
        estimator_instance.fit(X_train, y_train)
        y_proba = estimator_instance.predict_proba(X_test.iloc[indices])

        # assert probabilities are the same
        _assert_array_almost_equal(y_proba, expected_probas, decimal=2)
