from .utils import (  # isort:skip
    _lazy_generate_fwf,  # isort:skip
    _lazy_read_fwf,  # isort:skip
    data_to_csv,  # isort:skip
    data_to_fwf,  # isort:skip
    parse_spec_file,  # isort:skip
)


def read_fwf(spec_path, fwf_path, *args, **kwargs):
    """Takes specs and fwf file, parses it and returns a generator with parsed data

    Args:
        spec_path ([type]): [description]
        fwf_path ([type]): [description]

    Returns:
        [type]: [description]
    """
    fwf_specs = parse_spec_file(spec=spec_path)
    rows = _lazy_read_fwf(
        fwf_path=fwf_path,
        encoding=fwf_specs["FixedWidthEncoding"],
        offsets=fwf_specs["Offsets"],
        padding_char=fwf_specs["PaddingCharacter"],
        columnNames=fwf_specs["ColumnNames"],
    )
    return rows


def fwf_to_csv(spec_path, fwf_path, csv_path, sep="\t"):
    """Takes specs, fwf, csv_path, reads fwf and converts to csv

    Args:
        spec_path ([type]): [description]
        fwf_path ([type]): [description]
        csv_path ([type]): [description]
        sep (str, optional): [description]. Defaults to "\t".
    """
    fwf_specs = parse_spec_file(spec=spec_path)
    rows = read_fwf(spec_path=spec_path, fwf_path=fwf_path)
    data_to_csv(
        data=rows,
        csv_path=csv_path,
        header=fwf_specs["IncludeHeader"],
        sep=sep,
        encoding=fwf_specs["DelimitedEncoding"],
    )
    return


def generate_fwf_data(spec_path, length=None):
    fwf_specs = parse_spec_file(spec=spec_path)
    return _lazy_generate_fwf(
        characterSet=fwf_specs["characterSet"],
        columnNames=fwf_specs["ColumnNames"],
        offsets=fwf_specs["Offsets"],
        length=length,
    )


def generate_fwf_file(spec_path, fwf_path, length=None):
    fwf_specs = parse_spec_file(spec=spec_path)
    rows = generate_fwf_data(spec_path=spec_path, length=length,)

    data_to_fwf(
        data=rows,
        fwf_path=fwf_path,
        offsets=fwf_specs["Offsets"],
        header=fwf_specs["IncludeHeader"],
        padding_char=fwf_specs["PaddingCharacter"],
        encoding=fwf_specs["FixedWidthEncoding"],
    )
    return


class DataFrameF:
    """DataFrame to store Class
    """

    def __init__(self, spec_path=None):
        if spec_path:
            self.specs = parse_spec_file(spec=spec_path)
        else:
            self.specs = {}
        self.rows = []

    def _update_specs(self, spec_path=None):
        if spec_path:
            fwf_specs = parse_spec_file(spec=spec_path)
            self.specs = fwf_specs
            return
        elif self.specs:
            return
        else:
            raise SyntaxError("Specs are neither found in Df nor given.")
        return

    def read_fwf(
        self, fwf_path="", spec_path="",
    ):
        self._update_specs(spec_path=spec_path)
        self.rows = list(read_fwf(spec_path=spec_path, fwf_path=fwf_path,))
        return self

    def random_fwf_data(self, spec_path="", length=None):
        self._update_specs(spec_path=spec_path)
        self.rows = list(generate_fwf_data(spec_path=spec_path, length=length,))
        return self

    def to_csv(self, csv_path="", sep="\t"):
        data_to_csv(
            data=self.rows,
            csv_path=csv_path,
            header=self.specs.get("IncludeHeader", True),
            sep=sep,
            encoding=self.specs.get("DelimitedEncoding", None),
        )
        return

    def to_fwf(self, spec_path, fwf_path=""):
        fwf_specs = self._update_specs(spec_path=spec_path)
        data_to_fwf(
            data=self.rows,
            fwf_path=fwf_path,
            offsets=fwf_specs["Offsets"],
            header=fwf_specs["IncludeHeader"],
            padding_char=fwf_specs["PaddingCharacter"],
            encoding=fwf_specs["FixedWidthEncoding"],
        )
        return

    def __str__(self):
        return f"Specs: {self.specs}\nData: {self.rows[:10]}"  # noqa: E501

    def __repr__(self):
        return "\n".join(["\t".join(row) for row in self.rows[:5]])
