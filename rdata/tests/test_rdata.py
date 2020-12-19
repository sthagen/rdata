import os
import pathlib
import unittest
from fractions import Fraction

import numpy as np
import pandas as pd

import rdata

TESTDATA_PATH = rdata.TESTDATA_PATH


class SimpleTests(unittest.TestCase):

    def test_opened_file(self) -> None:
        parsed = rdata.parser.parse_file(open(TESTDATA_PATH /
                                              "test_vector.rda"))
        converted = rdata.conversion.convert(parsed)

        self.assertIsInstance(converted, dict)

    def test_opened_string(self) -> None:
        parsed = rdata.parser.parse_file(str(TESTDATA_PATH /
                                             "test_vector.rda"))
        converted = rdata.conversion.convert(parsed)

        self.assertIsInstance(converted, dict)

    def test_logical(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_logical.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_logical": np.array([True, True, False, True, False])
        })

    def test_vector(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_vector.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_vector": np.array([1., 2., 3.])
        })

    def test_empty_string(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_empty_str.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_empty_str": [""]
        })

    def test_complex(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_complex.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_complex": np.array([1 + 2j, 2, 0, 1 + 3j, -1j])
        })

    def test_matrix(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_matrix.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_matrix": np.array([[1., 2., 3.],
                                     [4., 5., 6.]])
        })

    def test_list(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_list.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_list":
                [
                    np.array([1.]),
                    ['a', 'b', 'c'],
                    np.array([2., 3.]),
                    ['hi']
                ]
        })

    def test_expression(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_expression.rda")
        converted = rdata.conversion.convert(parsed)

        np.testing.assert_equal(converted, {
            "test_expression": rdata.conversion.RExpression([
                rdata.conversion.RLanguage(['^', 'base', 'exponent'])])
        })

    def test_dataframe(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_dataframe.rda")
        converted = rdata.conversion.convert(parsed)

        pd.testing.assert_frame_equal(converted["test_dataframe"],
                                      pd.DataFrame({
                                          "class": pd.Categorical(
                                              ["a", "b", "b"]),
                                          "value": [1, 2, 3]
                                      }))

    def test_ts(self) -> None:
        parsed = rdata.parser.parse_file(TESTDATA_PATH / "test_ts.rda")
        converted = rdata.conversion.convert(parsed)

        pd.testing.assert_series_equal(converted["test_ts"],
                                       pd.Series({
                                           2000 + Fraction(2, 12): 1.,
                                           2000 + Fraction(3, 12): 2.,
                                           2000 + Fraction(4, 12): 3.,
                                       }))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
