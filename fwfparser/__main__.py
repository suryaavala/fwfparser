def main(spec, file=None, output=None, delimiter="\t"):
    """Parse fixed width files, convert them to csv and write them to 'output'

    Args:
        spec (str): path to json file describing the specs for fixed width file.
                    See: ../example/spec.json for format
        files (str): path to fix width file containing fixed width data.
                    Defaults to None,
                    then a random fwf is generated for parsing and save as "sample_fwf.txt".
        output (str): Path to file where parsed content(output) is written to (as delimited).
                      Defaults to None.
                      Then output's written to a file called "sample_fwf_parsed.csv";
                       in the same directory as spec.
        delimiter (str, optional): field delimiter for csv's/outputs. Defaults to "\t".
    """

    return


if __name__ == "__main__":
    main()
