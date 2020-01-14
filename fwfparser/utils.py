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
    """Generates a string of valid cp1252 characters

    Returns:
        str: string of all valid cp1252 characters
    """
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
    """Takes spec (as a dict or a path to spec file)

    Args:
        spec (dict, str): dict of specs or path to fwf spec file

    Raises:
        ValueError: Invalid format: Spec file, if the spec file does not meet minimum requirements
        ValueError: spec should be dict or str

    Returns:
        specs[dict]: valid specs + additional optional specs
    """
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
    """Takes string/line formatted as an fwf with given offsets and given padding char,
    parses it and return a row (list) with each column as an item

    Args:
        line (str, optional): fwf line to be parsed. Defaults to None.
        offsets (list[int], optional): length of each field in the fwf line. Defaults to None.
        padding_char (str, optional): padding character used in fwf. Defaults to " ".

    Raises:
        TypeError: if the line is not a string
        TypeError: if offsets are not a list
        ValueError: if lines are not the same length as offsets

    Returns:
        row[list[str]]: list of strings with each of them being the value in column
    """
    if not isinstance(line, str):
        raise TypeError(f"line should be a string")
    if not isinstance(offsets, list):
        raise TypeError(f"offsets should be a list")
    if not line:
        # NOTE Returns an empty list if the line is empty
        # empty rows should alteast have padding characters
        return []
    if len(line) != sum(offsets):
        raise ValueError("Lines should be of same length as sum of offsets")
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
    """Takes a header, rows and checks and removes if the first element of the rows is header

    Args:
        header_row (list[str]): list of column names - header
        rows (generator - list[list[str]]): list of list of string - data/rows

    Returns:
        rows[chain]: deduped rows - without header
    """
    try:
        dup = next(rows)
    except StopIteration:
        return rows
    if header_row == dup:
        return rows
    else:
        return chain([dup], rows)


def _lazy_read_fwf(fwf_path, encoding, offsets, padding_char, columnNames):
    """Reads and fwf file and returns a generator of parsed data

    Args:
        fwf_path (str): path to fwf file
        encoding (str): encoding of fwf file
        offsets (list[str]): lengths of each column in fwf
        padding_char (str): padding character uses in fwf to fill gaps
        columnNames (list[str]): names of each column in fwf

    Returns:
        rows[chain]: generator of header + data
    """
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
    """Writes data (list/generator) to a csv file

    Args:
        data (generator/list/chain): data to be written
        csv_path (str, optional): path to generate csv file at. Defaults to "".
        header (bool, optional): boolean to include header or not. Defaults to True.
        sep (str, optional): delimiter to be used in the csv. Defaults to "\t".
        encoding (str, optional): encoding of the csv file. Defaults to None.

    Raises:
        ValueError: if a path to csv is not given
        TypeError: if the data is not a list or generator/chain
    """
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
    """Generates a random fwf line

    Args:
        characterSet (str): valid to pick characters from
        offsets (list[int]): lengths of each field

    Returns:
        line(str): line formatted in fwf
    """
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
