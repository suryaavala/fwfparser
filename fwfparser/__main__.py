import sys


def main(spec, file=None, output=None, delimiter="\t"):
    """Parse fixed width files, convert them to csv and write them to 'output'

    Args:
        spec (str): path to json file describing the specs for fixed width file.
                    See: ../example/spec.json for format
        files (str): path to fix width file containing fixed width data.
                    Defaults to None, then a random fwf is generated for parsing.
        output (str): Path to file where parsed content(output) is written to (as delimited).
                      Defaults to None, then output's written to sys.stdout.
        delimiter (str, optional): field delimiter for csv's/outputs. Defaults to "\t".
    """
    if output is None:
        output = sys.stdout

    return


if __name__ == "__main__":
    main()
