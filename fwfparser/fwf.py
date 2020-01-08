# import random
from .utils import parse_spec_file, data_to_csv


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
            self._lazy_read_fwf(
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

    def _lazy_read_fwf(self, fwf_path, encoding, offsets, padding_char):
        return (
            self._parse_fwf_line(
                line=fwf_line.strip("\n"), offsets=offsets, padding_char=padding_char
            )
            for fwf_line in open(fwf_path, "r", encoding=encoding)
        )

    def _parse_fwf_line(self, line=None, offsets=None, padding_char=" "):
        if not isinstance(line, str):
            raise TypeError(f"line should be a string")
        if not isinstance(offsets, list):
            raise TypeError(f"offsets should be a list")
        row = []
        idx_at = 0
        for col_offset in offsets:
            row.append(
                line[idx_at : int(col_offset) + idx_at].strip(  # noqa: E203 \
                    padding_char
                )
            )
            idx_at += int(col_offset)
        return row


def read_fwf(spec_path, fwf_path, *args, **kwargs):
    return DataFrameF().read_fwf(spec_path=spec_path, fwf_path=fwf_path)
