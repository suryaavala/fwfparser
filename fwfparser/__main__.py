import os

from .fwf import fwf_to_csv, generate_fwf_file

SAMPLE_OUTPUT = "./sample_output.csv"
SAMPLE_INPUT = "./sample_fwf.txt"


def main(spec, fwf=None, output=None, delimiter="\t"):
    """Parse fixed width files, convert them to csv and write them to 'output'

    Args:
        spec (str): path to json file describing the specs for fixed width file.
                    See: ../example/spec.json for format
        files (str): path to fix width file containing fixed width data.
                    Defaults to None,
                    then a random fwf is generated for parsing and save as "sample_fwf.txt".
        output (str): Path to file where parsed content(output) is written to (as delimited).
                      Defaults to None.
                      Then output's written to a file called "sample_output.csv";
                       in the same directory as spec.
        delimiter (str, optional): field delimiter for csv's/outputs. Defaults to "\t".
    """
    if fwf is None:
        fwf = SAMPLE_INPUT
        generate_fwf_file(spec_path=spec, fwf_path=fwf, length=10)
    elif not os.path.isfile(fwf):
        generate_fwf_file(spec_path=spec, fwf_path=fwf, length=10)
    # NOTE: IF we get an empty fwf file then we should return an empty csv
    #       An empty file should have a \n or size == 0 and return \n or size == 0 respectively

    #  So if we want to treat  size==0 as the user asking us to generate a random fwf then
    # elif os.stat(fwf).st_size == 0:
    #     generate_fwf_file(spec_path=spec, fwf_path=fwf, length=10)
    if output is None:
        output = SAMPLE_OUTPUT

    fwf_to_csv(spec_path=spec, fwf_path=fwf, csv_path=output, sep=delimiter)
    return


if __name__ == "__main__":
    # python -m fixwidth data.layout data1.txt data2.txt
    import argparse

    argp = argparse.ArgumentParser(
        prog="fwfparser",
        description="Generate, Read and Covnert fixed width files to CSV",
    )
    argp.add_argument(
        "-s", "--spec", required=True, help="Path to file with fwf specifications"
    )
    argp.add_argument(
        "-f",
        "--fwf",
        default=None,
        help='Path to fwf data file \
        (default - generates a random fwf at "./sample_fwf.txt")',
    )
    argp.add_argument("-d", "--delimiter", default="\t", help="Field separator")
    argp.add_argument(
        "-o",
        "--output",
        default=None,
        help='Path to output CSV file (default "./sample_output.csv")',
    )

    options = argp.parse_args()
    print(options)
    main(
        spec=options.spec,
        fwf=options.fwf,
        output=options.output,
        delimiter=options.delimiter,
    )
