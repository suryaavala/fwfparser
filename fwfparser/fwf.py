# import random
from .utils import _lazy_read_fwf, data_to_csv, parse_spec_file


class DataFrameF:
    """DataFrame to store Class
    """

    def __init__(self):
        self.delim_encoding = None
        self.header = None
        self.rows = []

    def read_fwf(self, spec_path="", fwf_path=""):
        fwf_specs = parse_spec_file(spec=spec_path)
        self.header = fwf_specs["IncludeHeader"].lower().title()
        self.delim_encoding = fwf_specs["DelimitedEncoding"]
        self.rows = list(
            _lazy_read_fwf(
                fwf_path=fwf_path,
                encoding=fwf_specs["FixedWidthEncoding"],
                offsets=fwf_specs["Offsets"],
                padding_char=fwf_specs["PaddingCharacter"],
            )
        )
        return self

    def to_csv(self, csv_path="", sep="\t"):
        data_to_csv(
            data=self.rows,
            csv_path=csv_path,
            header=self.header,
            sep=sep,
            encoding=self.delim_encoding,
        )
        return

    def __str__(self):
        return f"Header: {self.header}\nEncoding for Delimiter: {self.delim_encoding}\nData: {self.rows[:10]}"  # noqa: E501

    def __repr__(self):
        return "\n".join(["\t".join(row) for row in self.rows[:5]])


def read_fwf(spec_path, fwf_path, *args, **kwargs):
    return DataFrameF().read_fwf(spec_path=spec_path, fwf_path=fwf_path)


def fwf_to_csv(spec_path, fwf_path, csv_path, sep="\t"):
    fwf_specs = parse_spec_file(spec=spec_path)
    rows = _lazy_read_fwf(
        fwf_path=fwf_path,
        encoding=fwf_specs["FixedWidthEncoding"],
        offsets=fwf_specs["Offsets"],
        padding_char=fwf_specs["PaddingCharacter"],
    )
    data_to_csv(
        data=rows,
        csv_path=csv_path,
        header=fwf_specs["IncludeHeader"],
        sep=sep,
        encoding=fwf_specs["DelimitedEncoding"],
    )
    return
