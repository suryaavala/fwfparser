import sys


def main(spec, files=None, output=None, delimiter="\t"):
    """Parse fixed width files, convert them to csv and write them to 'output'

    Arguments:
        spec {str} -- path to file describing the specs for fixed width file.
        See: ../specs/spec.json

    Keyword Arguments:
        file {str} -- path to fix width file containing data.
                    If nothing is given, then a random fwf is generated for parsing
        output {str} -- Path to file where parsed content(output) is written to.
                    If nothing's given, then output's written to sys.stdout (default: {sys.stdout})
        delimiter {str} -- field delimiter for csv's/outputs (default: {'\t'})
    """
    if output is None:
        output = sys.stdout

    return


if __name__ == "__main__":
    main()
