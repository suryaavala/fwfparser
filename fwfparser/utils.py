import json
import sys
import types


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
OPTIONAL_SPECS = {
    "Alignment": "left",
    "PaddingCharacter": " ",
    "characterSet": valid_cp1252_charInts(),
}


def parse_spec_file(spec):
    with open(str(spec), "r") as spec_file:
        try:
            specs = json.loads(spec_file.read())
        except ValueError:
            raise ValueError("Invalid format: Spec file")
    return validate_specs(specs)


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
    try:
        specs["Offsets"] = list(map(int, specs["Offsets"]))
    except ValueError:
        raise ValueError("Not able to convert offsets to ints")
    OPTIONAL_SPECS.update(specs)
    return OPTIONAL_SPECS


def data_to_csv(
    data, csv_path="", header=True, sep="\t", encoding=sys.getdefaultencoding()
):
    if not csv_path:
        raise ValueError("path to csv should be given")
    if not isinstance(data, (list, types.GeneratorType)):
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
        # csv_writer.writerows(data)
        for d in data:
            csv_file.write("\n" + sep.join(d))
    return
