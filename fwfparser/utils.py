import json
import random
import sys
import types
import warnings
from itertools import chain

MIN_SPECS = [
    "ColumnNames",
    "Offsets",
    "FixedWidthEncoding",
    "IncludeHeader",
    "DelimitedEncoding",
]
SUPPORTED_ENCODINGS = {
    "FixedWidthEncoding": ["windows-1252", "cp1252"],
    "DelimitedEncoding": ["utf-8"],
}
SPEC_HEADER = ["True", "False"]


def valid_cp1252_charInts():
    # Good resource: http://string-functions.com/encodingtable.aspx?encoding=65001&decoding=1252
    # According to: https://unicode.org/Public/MAPPINGS/VENDORS/MICSFT/WINDOWS/CP1252.TXT
    # filter_chars = undefined_characters + \
    #  unicode error chars + \
    # control_characters
    filter_chars = (
        [129, 141, 143, 144, 157] + [193, 205, 207, 208, 221] + list(range(33)) + [127]
    )
    charset = ""
    for i in range(256):
        if i in filter_chars:
            pass
        else:
            charset += chr(i).encode("utf-8").decode("cp1252")
    return charset


OPTIONAL_SPECS = {
    "Alignment": "left",
    "PaddingCharacter": " ",
    "characterSet": valid_cp1252_charInts(),
}


def parse_spec_file(spec):
    if isinstance(spec, dict):
        # TODO: Does accept dict but this functionality is not bubbled up
        return validate_specs(spec)
    elif isinstance(spec, str):
        with open(str(spec), "r") as spec_file:
            try:
                specs = json.loads(spec_file.read())
            except ValueError:
                raise ValueError("Invalid format: Spec file")
        return validate_specs(specs)
    else:
        raise ValueError("spec should be dict or str")


def validate_specs(specs=None):
    """Verify specs are correct and
    atleast have
    [ "ColumnNames","Offsets", "FixedWidthEncoding",
        "IncludeHeader", "DelimitedEncoding"]

    Args:
        specs (dict, optional): specs dict from spec file. Defaults to None.

    Returns:
        None or specs: specs if valid
    """
    if specs is None:
        raise ValueError("Invalid Spec file")
    if set(MIN_SPECS) != set(specs.keys()):
        raise ValueError("Minimum Specs not met")
    if len(specs["ColumnNames"]) != len(specs["Offsets"]):
        raise ValueError("Number of ColumnNames should be equal to number of offsets")
    if len(specs["ColumnNames"]) <= 0:
        raise ValueError("Atleast one columnname/one offset should be given")
    if specs["FixedWidthEncoding"] not in SUPPORTED_ENCODINGS["FixedWidthEncoding"]:
        raise ValueError(
            f"Only supports encodings: {SUPPORTED_ENCODINGS['FixedWidthEncoding']}"
        )
    if specs["DelimitedEncoding"] not in SUPPORTED_ENCODINGS["DelimitedEncoding"]:
        raise ValueError(
            f"Only supports encodings: {SUPPORTED_ENCODINGS['DelimitedEncoding']}"
        )
    if specs["IncludeHeader"] not in SPEC_HEADER:
        raise ValueError(f"IncludeHeader can only be: {SPEC_HEADER}")
    elif specs["IncludeHeader"].lower() == "true":
        specs["IncludeHeader"] = True
    else:
        specs["IncludeHeader"] = False
    try:
        specs["Offsets"] = list(map(int, specs["Offsets"]))
    except ValueError:
        raise ValueError("Not able to convert offsets to ints")
    specs["ColumnNames"] = list(map(str, specs["ColumnNames"]))
    for nb in range(len(specs["Offsets"])):
        if len(str(specs["ColumnNames"][nb])) > int(specs["Offsets"][nb]):
            warnings.warn(
                f"{specs['ColumnNames'][nb]} is larger than it's offset, so chopping it off!"
            )
        if specs["Offsets"][nb] < 0:
            raise ValueError("Offsets can not be negative")
    OPTIONAL_SPECS.update(specs)
    return OPTIONAL_SPECS


def _parse_fwf_line(line=None, offsets=None, padding_char=" "):
    if not isinstance(line, str):
        raise TypeError(f"line should be a string")
    if not isinstance(offsets, list):
        raise TypeError(f"offsets should be a list")
    if not line:
        # NOTE Returns an empty list if the line is empty
        # empty rows should alteast have padding characters
        return []
    # NOTE if a line ends with padding character,
    # then it is considered as padding character and removed
    row = []
    idx_at = 0
    for col_offset in offsets:
        row.append(
            line[idx_at : int(col_offset) + idx_at].rstrip(padding_char)  # noqa: E203 \
        )
        idx_at += int(col_offset)
    return row


def _dedup_header(header_row, rows):
    try:
        dup = next(rows)
    except StopIteration:
        return rows
    if header_row == dup:
        return rows
    else:
        return chain([dup], rows)
    return


def _lazy_read_fwf(fwf_path, encoding, offsets, padding_char, columnNames):
    header = [columnNames]
    rows = (
        _parse_fwf_line(
            line=fwf_line.rstrip("\n"), offsets=offsets, padding_char=padding_char
        )
        for fwf_line in open(fwf_path, "r", encoding=encoding)
    )
    rows = _dedup_header(header[0], rows)
    return chain(header, rows)


def data_to_csv(data, csv_path="", header=True, sep="\t", encoding=None):
    if encoding is None:
        encoding = sys.getdefaultencoding()
    if not csv_path:
        raise ValueError("path to csv should be given")
    if not isinstance(data, (list, types.GeneratorType, chain)):
        raise TypeError("data must be a list or generator")
    with open(csv_path, "w", encoding=encoding) as csv_file:
        # csv_writer = csv.writer(
        #     csv_file, delimiter=sep, escapechar='//', quoting=csv.QUOTE_NONE)
        if isinstance(data, list):
            head = data[0]
            data = data[1:]
        else:
            head = next(data)
        if header:
            # csv_writer.writerow(head)
            csv_file.write(sep.join(head))
            csv_file.write("\n")
        # csv_writer.writerows(data)
        for d in data:
            csv_file.write(sep.join(d) + "\n")
    return


def _generate_fwf_row(characterSet, offsets):
    return [
        "".join(random.choices(characterSet, k=random.randint(0, off)))  # nosec
        for off in offsets
    ]


def _lazy_generate_fwf(characterSet, offsets, columnNames, length=None):
    if length is None:
        length = random.randint(1, 1000)  # nosec
    header = [columnNames]
    rows = (
        _generate_fwf_row(characterSet=characterSet, offsets=offsets)
        for _ in range(length)
    )
    return chain(header, rows)


def _row_to_line(row, offsets, padding_char):
    padded_row = ""
    for nb, text in enumerate(row):
        text_length = len(text)
        offset = int(offsets[nb])
        if text_length <= offset:
            padded_row += text + padding_char * (offset - text_length)
        if text_length > offset:
            padded_row += text[:offset]
    return padded_row


def data_to_fwf(
    data, fwf_path="", offsets=None, header=True, padding_char="\t", encoding=None,
):
    if encoding is None:
        encoding = sys.getdefaultencoding()
    if not fwf_path:
        raise ValueError("path to csv should be given")
    if not isinstance(data, (list, types.GeneratorType, chain)):
        raise TypeError("data must be a list or generator")
    if offsets is None:
        raise ValueError("offsets must be given")

    with open(fwf_path, "w", encoding=encoding) as fwf_file:
        # csv_writer = csv.writer(
        #     csv_file, delimiter=sep, escapechar='//', quoting=csv.QUOTE_NONE)
        if isinstance(data, list):
            head = data[0]
            data = data[1:]
        else:
            head = next(data)
        if header:
            # csv_writer.writerow(head)
            fwf_file.write(
                _row_to_line(row=head, offsets=offsets, padding_char=padding_char)
            )
            fwf_file.write("\n")
        # csv_writer.writerows(data)
        for d in data:
            fwf_file.write(
                _row_to_line(row=d, offsets=offsets, padding_char=padding_char) + "\n"
            )

    return
