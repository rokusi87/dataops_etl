import json
import os
import pytest
import pandas as pd


# ---------------------------------------------------------------------------
# In-memory DataFrame fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_df():
    return pd.DataFrame({"id": [1, 2, 3], "amount": [100.0, 200.0, 300.0]})


@pytest.fixture
def df_with_duplicates():
    return pd.DataFrame({"id": [1, 1, 3], "amount": [100.0, 100.0, 300.0]})


@pytest.fixture
def df_with_negatives():
    return pd.DataFrame({"id": [1, 2, 3], "amount": [100.0, -50.0, 300.0]})


@pytest.fixture
def df_with_bad_types():
    return pd.DataFrame({"id": [1, 2, 3], "amount": ["abc", "N/A", 100.0]})


@pytest.fixture
def df_missing_columns():
    return pd.DataFrame({"name": ["Alice", "Bob"], "price": [100, 200]})


@pytest.fixture
def empty_df():
    return pd.DataFrame({"id": [], "amount": []})


# ---------------------------------------------------------------------------
# Temp file fixtures (write to tmp_path so tests stay isolated)
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_csv(tmp_path):
    p = tmp_path / "valid.csv"
    p.write_text("id,amount\n1,100\n2,200\n3,300\n")
    return str(p)


@pytest.fixture
def pipe_delimited_txt(tmp_path):
    p = tmp_path / "pipe.txt"
    p.write_text("id|amount\n1|100\n2|200\n")
    return str(p)


@pytest.fixture
def valid_json(tmp_path):
    p = tmp_path / "valid.json"
    data = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
    p.write_text(json.dumps(data))
    return str(p)


@pytest.fixture
def schema_error_csv(tmp_path):
    p = tmp_path / "schema_error.csv"
    p.write_text("name,price\nAlice,100\nBob,200\n")
    return str(p)


@pytest.fixture
def negative_csv(tmp_path):
    p = tmp_path / "negative.csv"
    p.write_text("id,amount\n1,-100\n2,200\n")
    return str(p)


@pytest.fixture
def type_error_csv(tmp_path):
    p = tmp_path / "type_error.csv"
    p.write_text("id,amount\n1,abc\n2,200\n")
    return str(p)


@pytest.fixture
def duplicate_csv(tmp_path):
    p = tmp_path / "duplicate.csv"
    p.write_text("id,amount\n1,100\n1,200\n3,300\n")
    return str(p)


@pytest.fixture
def data_dir_with_files(tmp_path, valid_csv, schema_error_csv):
    """A temp data directory containing one SUCCESS and one FAILURE file."""
    import shutil
    d = tmp_path / "data"
    d.mkdir()
    shutil.copy(valid_csv, d / "good.csv")
    shutil.copy(schema_error_csv, d / "bad.csv")
    return str(d)
