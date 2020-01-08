import pytest
from fwfparser.__main__ import main
from fwfparser.fwf import read_fwf, DataFrameF
import json

# import os

VALID_SPEC_FILE = "tests/test_spec_valid.json"
VALID_FWF_FILE = "tests/test_fwf_valid.txt"
VALID_CSV_FILE = "tests/test_csv_valid.csv"


class TestMainPath:
    def test_no_spec_file_exception_main(self):
        """Test that an exception is raised when no path to spec file is not given from main()
        """
        with pytest.raises(TypeError) as error:
            assert main()
        assert (
            str(error.value) == "main() missing 1 required positional argument: 'spec'"
        )

    # def test_main_defaults(self):
    #     """Test that the package defaults to generating a random fwf file and converting it to csv
    #     """
    #     main(spec=VALID_SPEC_FILE)
    #     files = os.listdir(".")
    #     assert "sample_fwf.txt" in files
    #     assert "sample_fwf_parsed.csv" in files


class TestReadfwf:
    def test_no_specread_fwf(self):
        """Test that an exception is raised when no path to spec file is not given from read_fwf()
        """
        with pytest.raises(TypeError) as error:
            assert read_fwf()
        assert (
            str(error.value)
            == "read_fwf() missing 2 required positional arguments: 'spec_path' and 'fwf_path'"
        )

    def testread_fwf_output_type(self):
        """Test that read_fwf() returns an instance of class fwf()
        """
        assert isinstance(
            read_fwf(spec_path=VALID_SPEC_FILE, fwf_path=VALID_FWF_FILE), DataFrameF
        )

    def test_no_fwf(self):
        """Test that an exception is raised when no path to spec file is not given from read_fwf()
        """
        with pytest.raises(Exception) as error:
            assert read_fwf(spec_path=VALID_SPEC_FILE, fwf_path="")

        assert "[Errno 2] No such file or directory:" in str(error.value)


class TestDataFrameF:
    def test_DataFrameF_struct(self):
        df = DataFrameF()
        assert isinstance(df.rows, list)

    def test_invalid_spec_file(self):
        with pytest.raises(ValueError):
            assert DataFrameF().read_fwf(spec_path="tests/test_spec_invalid_json.json")

    def test_valid_spec_file(self):
        assert isinstance(
            DataFrameF().read_fwf(spec_path=VALID_SPEC_FILE, fwf_path=VALID_FWF_FILE),
            DataFrameF,
        )

    def test_not_min_specs(self, tmpdir):
        with open("tests/test_spec_invalid_minimum.json", "r") as specs_file:
            specs = json.loads(specs_file.read())
        for spec_number in specs:
            path = "test.json"
            with open(path, "w") as tmp_file:
                tmp_file.write(json.dumps(specs[spec_number]))
            with pytest.raises(ValueError):
                assert DataFrameF().read_fwf(spec_path=path)

    def test_parse(self, tmpdir):
        DataFrameF().read_fwf(
            spec_path=VALID_SPEC_FILE, fwf_path=VALID_FWF_FILE
        ).to_csv("test_generated_csv.csv")
        with open(VALID_CSV_FILE, "r") as v:
            valid = v.read()
        with open("test_generated_csv.csv", "r") as g:
            generated = g.read()
        assert valid == generated


# TODO: Column name is bigger than the offset?
