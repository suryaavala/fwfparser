import json
import os
import types
from itertools import chain

import pytest
from fwfparser.__main__ import main
from fwfparser.fwf import DataFrameF, fwf_to_csv, read_fwf

DEFAULT_OUTPUT = "sample_output.csv"
DEFAULT_INPUT = "sample_fwf.txt"

VALID_SPEC_FILE = "tests/test_spec_valid.json"
VALID_FWF_FILE = "tests/test_fwf_valid.txt"
VALID_CSV_FILE = "tests/test_csv_valid.csv"
VALID_CSV_NLN_FILE = "tests/test_csv_valid_nln.csv"

TMP_CSV = "test.csv"
TMP_FWF = "test.txt"
TMP_SPECS = "test.json"

# TODO tmpdir


def are_these_same(string1, string2):
    if os.path.isfile(string1):
        with open(string1, "r") as v:
            string1 = v.read()
    if os.path.isfile(string2):
        with open(string2, "r") as g:
            string2 = g.read()
    # print(f"s1:{string1}.\ns2:{string2}.")
    return string1 == string2


def change_these_in_valid_specs(changes):
    with open(VALID_SPEC_FILE, "r") as v:
        specs = json.loads(v.read())
    with open(TMP_SPECS, "w") as t:
        specs.update(changes)
        t.write(json.dumps(specs))
    return


class TestMainPath:
    def test_main_no_spec_file_exception(self):
        """An exception is raised when no path to spec file is not given to main()
        """
        with pytest.raises(TypeError) as error:
            assert main()
        assert (
            str(error.value) == "main() missing 1 required positional argument: 'spec'"
        )

    def test_main_defaults_generates_files(self):
        """When a valid spec file is given:
            1. A random "./sample_fwf.txt" should be generated
            2. And parsed to "./sample_fwf_parsed.csv"
        Test that these are being generated
        """
        main(spec=VALID_SPEC_FILE)
        files = os.listdir(".")
        print(files)
        assert DEFAULT_INPUT in files
        assert DEFAULT_OUTPUT in files

    def test_main_defaults_generates_iles(self):
        """When a valid spec file is given:
            1. A random "./sample_fwf.txt" should be generated
            2. And parsed to "./sample_fwf_parsed.csv"
        Test that these are being generated
        """
        main(spec=VALID_SPEC_FILE, output="sample_fwf_parsed.csv")
        files = os.listdir(".")
        with open("sample_fwf_parsed.csv", "r", encoding="utf-8") as c:
            csv_lines = c.readlines()
            csv_len = len(csv_lines)
            # csv_size = sum([len(_) for _ in csv_lines])
        with open("sample_fwf.txt", "r", encoding="cp1252") as f:
            fwf_lines = f.readlines()
            fwf_len = len(fwf_lines)
            fwf_size = sum([len(_) for _ in fwf_lines])
        with open(VALID_SPEC_FILE, "r") as s:
            spec = json.loads(s.read())
            offsets = list(map(int, spec["Offsets"]))

        assert "sample_fwf.txt" in files
        assert "sample_fwf_parsed.csv" in files
        assert fwf_size == (sum(offsets) + 1) * fwf_len
        assert csv_len == fwf_len == 11
        assert sum([len(_.replace("\t", "")) for _ in csv_lines]) == sum(
            [len(_.replace(" ", "")) for _ in fwf_lines]
        )

    def test_main_vaild_parsing(self):
        """When a valid spec file and valid fwf are given:
            1. fwf should be parsed and a csv should be generated
            2. generated csv should match our valid csv
        """
        main(spec=VALID_SPEC_FILE, fwf=VALID_FWF_FILE, output=TMP_CSV)
        assert are_these_same(VALID_CSV_FILE, TMP_CSV)

    def test_main_custom_delimiter(self):
        """When a valid spec file, valid fwf and a CUSTOM DELIMITER are given:
            1. A csv with CUSTOM DELIMITED should be generated
        """
        main(spec=VALID_SPEC_FILE, fwf=VALID_FWF_FILE, output=TMP_CSV, delimiter="\n")
        assert are_these_same(VALID_CSV_NLN_FILE, TMP_CSV)

    def test_main_blankfiles(self):
        """When a valid spec file, blank fwf are given:
            1. A random "./sample_fwf.txt" should be generated
            2. And parsed to "./sample_fwf_parsed.csv"
        Test that these are being generated
        """
        with open(TMP_FWF, "w") as t:
            t.write("")
        main(
            spec=VALID_SPEC_FILE, fwf=TMP_FWF, output=TMP_CSV,
        )
        assert are_these_same(TMP_CSV, "f1\tf2\tf3\tf4\tf5\tf6\tf7\tf8\tf9\tf10\n")

    def test_main_emptyfiles(self):
        """When a valid spec file with header included, empty fwf are given:
            1. A csv with just header should be generated
        """
        with open(TMP_FWF, "w") as t:
            t.write("\n")
        main(
            spec=VALID_SPEC_FILE, fwf=TMP_FWF, output=TMP_CSV,
        )
        assert are_these_same(TMP_CSV, "f1\tf2\tf3\tf4\tf5\tf6\tf7\tf8\tf9\tf10\n\n")

    def test_main_noheader(self):
        """When a valid spec file with no header and valid fwf are given:
            1. fwf should be parsed and a csv should be generated
            2. generated csv should match our valid csv
        """
        with open(TMP_FWF, "w") as t:
            t.write("\n")
        change_these_in_valid_specs({"IncludeHeader": "False"})
        main(
            spec=TMP_SPECS, fwf=TMP_FWF, output=TMP_CSV,
        )
        assert are_these_same(TMP_CSV, "\n")

    # TODO Encoding tests?


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
            read_fwf(spec_path=VALID_SPEC_FILE, fwf_path=VALID_FWF_FILE),
            (types.GeneratorType, chain),
        )

    def test_no_fwf(self):
        """Test that an exception is raised when no path to spec file is not given from read_fwf()
        """
        with pytest.raises(Exception) as error:
            assert read_fwf(spec_path=VALID_SPEC_FILE, fwf_path="")

        assert "[Errno 2] No such file or directory:" in str(error.value)

    def test_readfwf(self):
        rows = read_fwf(spec_path=VALID_SPEC_FILE, fwf_path=VALID_FWF_FILE)

        with open(VALID_CSV_FILE, "r") as v:
            valid = list(map(lambda x: x.split("\t"), v.read().splitlines()))

        assert list(rows) == valid

    def test_parse(self, tmpdir):
        fwf_to_csv(
            spec_path=VALID_SPEC_FILE,
            fwf_path=VALID_FWF_FILE,
            csv_path="test_generated_csv.csv",
        )
        with open(VALID_CSV_FILE, "r") as v:
            valid = v.read()
        with open("test_generated_csv.csv", "r") as g:
            generated = g.read()
        assert valid == generated


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
            if spec_number not in ["1", "2", "3", "4", "5"]:
                continue
            path = "test.json"
            with open(path, "w") as tmp_file:
                tmp_file.write(json.dumps(specs[spec_number]))
            with pytest.raises(ValueError):
                assert DataFrameF().read_fwf(spec_path=path, fwf_path=VALID_FWF_FILE)

    def test_colnames_larger(self):
        with open("tests/test_spec_invalid_minimum.json", "r") as specs_file:
            specs = json.loads(specs_file.read())["mycolumn"]
        path = "mycolumn.json"
        with open(path, "w") as tmp_file:
            tmp_file.write(json.dumps(specs))
        with pytest.warns(UserWarning) as warn:
            assert DataFrameF().read_fwf(spec_path=path, fwf_path=VALID_FWF_FILE)
        assert "mycolumn is larger than it's offset, so chopping it off!" in str(
            warn[0].message.args[0]
        )

    def test_parse(self, tmpdir):
        DataFrameF().read_fwf(
            spec_path=VALID_SPEC_FILE, fwf_path=VALID_FWF_FILE
        ).to_csv("test_generated_csv.csv")
        with open(VALID_CSV_FILE, "r") as v:
            valid = v.read()
        with open("test_generated_csv.csv", "r") as g:
            generated = g.read()
        assert valid == generated


# TODO what happens when a row of just padding characters
