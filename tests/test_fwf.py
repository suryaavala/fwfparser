import pytest
from fwfparser.__main__ import main
from fwfparser.fwf import read_fwf, DataFrameF
import json


class TestMainPath:
    def test_no_spec_file_exception_main(self):
        """Test that an exception is raised when no path to spec file is not given from main()
        """
        with pytest.raises(TypeError) as error:
            assert main()
        assert (
            str(error.value) == "main() missing 1 required positional argument: 'spec'"
        )


class TestReadfwf:
    def test_no_spec_read_fwf(self):
        """Test that an exception is raised when no path to spec file is not given from read_fwf()
        """
        with pytest.raises(TypeError) as error:
            assert read_fwf()
        assert (
            str(error.value)
            == "read_fwf() missing 1 required positional argument: 'spec'"
        )

    def test_read_fwf_output_type(self):
        """Test that read_fwf() returns an instance of class fwf()
        """
        assert isinstance(read_fwf(spec="tests/test_spec_valid.json"), DataFrameF)


class TestDataFrameF:
    def test_DataFrameF_struct(self):
        df = DataFrameF()
        assert isinstance(df.columns, list)
        assert isinstance(df.rows, list)

    def test_invalid_spec_file(self):
        with pytest.raises(ValueError):
            assert DataFrameF(spec="tests/test_spec_invalid_json.json")

    def test_valid_spec_file(self):
        assert isinstance(read_fwf(spec="tests/test_spec_valid.json"), DataFrameF)

    def test_not_min_specs(self, tmpdir):
        with open("tests/test_spec_invalid_minimum.json", "r") as specs_file:
            specs = json.loads(specs_file.read())
        for spec_number in specs:
            path = "test.json"
            with open(path, "w") as tmp_file:
                tmp_file.write(json.dumps(specs[spec_number]))
            with pytest.raises(ValueError):
                assert DataFrameF(spec=path)
