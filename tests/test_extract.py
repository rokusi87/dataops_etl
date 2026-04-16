import pytest
import pandas as pd
from etl.extract import detect_delimiter, read_file


class TestDetectDelimiter:
    def test_comma_delimiter(self, valid_csv):
        assert detect_delimiter(valid_csv) == ","

    def test_pipe_delimiter(self, pipe_delimited_txt):
        assert detect_delimiter(pipe_delimited_txt) == "|"


class TestReadFile:
    def test_reads_csv(self, valid_csv):
        df = read_file(valid_csv)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["id", "amount"]
        assert len(df) == 3

    def test_reads_pipe_txt(self, pipe_delimited_txt):
        df = read_file(pipe_delimited_txt)
        assert "id" in df.columns
        assert "amount" in df.columns
        assert len(df) == 2

    def test_reads_json(self, valid_json):
        df = read_file(valid_json)
        assert isinstance(df, pd.DataFrame)
        assert "id" in df.columns
        assert len(df) == 2

    def test_unsupported_format_raises(self, tmp_path):
        p = tmp_path / "data.parquet"
        p.write_bytes(b"fake parquet content")
        with pytest.raises(Exception, match="Unsupported format"):
            read_file(str(p))

    def test_csv_returns_correct_values(self, valid_csv):
        df = read_file(valid_csv)
        assert df["amount"].tolist() == [100, 200, 300]
        assert df["id"].tolist() == [1, 2, 3]
