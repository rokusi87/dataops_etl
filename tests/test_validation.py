import pytest
import pandas as pd
from utils.validation_rules import validate_data


class TestSchemaValidation:
    def test_passes_with_required_columns(self, valid_df):
        errors = validate_data(valid_df)
        assert errors == []

    def test_fails_missing_both_columns(self, df_missing_columns):
        errors = validate_data(df_missing_columns)
        assert len(errors) == 1
        assert errors[0]["type"] == "SCHEMA_ERROR"
        assert "id" in errors[0]["message"]
        assert "amount" in errors[0]["message"]

    def test_fails_missing_amount_only(self):
        df = pd.DataFrame({"id": [1, 2], "price": [100, 200]})
        errors = validate_data(df)
        assert any(e["type"] == "SCHEMA_ERROR" for e in errors)

    def test_schema_error_stops_further_validation(self, df_missing_columns):
        errors = validate_data(df_missing_columns)
        # Only one error returned — validation halts early
        assert len(errors) == 1


class TestDataTypeValidation:
    def test_fails_non_numeric_amounts(self, df_with_bad_types):
        errors = validate_data(df_with_bad_types)
        assert any(e["type"] == "DATA_TYPE_ERROR" for e in errors)

    def test_type_error_stops_further_validation(self, df_with_bad_types):
        errors = validate_data(df_with_bad_types)
        # Type check halts — no downstream errors expected
        types = [e["type"] for e in errors]
        assert "VALUE_ERROR" not in types
        assert "DUPLICATE_ERROR" not in types

    def test_numeric_strings_pass(self):
        df = pd.DataFrame({"id": [1, 2], "amount": ["100", "200"]})
        errors = validate_data(df)
        assert errors == []


class TestNegativeValueValidation:
    def test_fails_negative_amounts(self, df_with_negatives):
        errors = validate_data(df_with_negatives)
        assert any(e["type"] == "VALUE_ERROR" for e in errors)

    def test_zero_amount_passes(self):
        df = pd.DataFrame({"id": [1, 2], "amount": [0.0, 100.0]})
        errors = validate_data(df)
        assert errors == []

    def test_all_negative_raises_value_error(self):
        df = pd.DataFrame({"id": [1, 2], "amount": [-10, -20]})
        errors = validate_data(df)
        assert any(e["type"] == "VALUE_ERROR" for e in errors)


class TestDuplicateValidation:
    def test_fails_duplicate_ids(self, df_with_duplicates):
        errors = validate_data(df_with_duplicates)
        assert any(e["type"] == "DUPLICATE_ERROR" for e in errors)

    def test_unique_ids_pass(self, valid_df):
        errors = validate_data(valid_df)
        assert not any(e["type"] == "DUPLICATE_ERROR" for e in errors)

    def test_multiple_errors_reported_together(self):
        df = pd.DataFrame({"id": [1, 1, 2], "amount": [-10, -20, 300]})
        errors = validate_data(df)
        types = [e["type"] for e in errors]
        assert "VALUE_ERROR" in types
        assert "DUPLICATE_ERROR" in types


class TestEmptyDataFrame:
    def test_empty_df_passes_validation(self, empty_df):
        errors = validate_data(empty_df)
        assert errors == []
