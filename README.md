## fwfparser

A python package to parse fixed width files

## Quick Start

1.  docker
2.  log into dockerhub `docker login`

#### Test fwfparser

1.  Build and test locally: `./test_fwfparser.sh local`
2.  Pull image from dockerhub and run tests: `./test_fwfparser.sh`

#### Generate/Parse FWF Files

Generate, parse and convert <b>random</b> sample files:

- Uses `./example/spec.json`
- generates a random `./example/<timestamp>/sample_input.txt` and
- converts it to `./example/<timestamp>/sample_output.csv`

1. Build and run locally with default args:
   `./generate_parse_files.sh local`
2. Pull image from dockerhub and run with default args:
   `./generate_parse_files.sh`

Generate, parse and convert <b>desired</b> files:

- Uses `.` to bind and generate outputfile in
- Uses `-s <spec>` as specs (relative path to dir above)
- Parses `-f <fwf>` (relative path to dir above)
- Outputs to `-o <out>` (relative path to dir above)

Run docker container with all options:
`./generate_parse_files.sh local . -s example/spec.json -f example/fwf.txt -o example/my_output.csv -d "\t"`

```
Usage:
./generate_parse_files.sh
 "local"        - optional keyword argument to specify whether to build the docker image locally or pull it from docker hub
 dir            - local directory to bind to docker container and generate files in
 fwfparser args - arguments that will be passed onto fwfparser
                  -h, --help            show this help message and exit
                  -s SPEC, --spec SPEC  Path to file with fwf specifications
                  -f FWF, --fwf FWF     Path to fwf data file (default - generates a random
                        fwf at "./sample_fwf.txt")
                  -d DELIMITER, --delimiter DELIMITER
                        Field separator
                  -o OUTPUT, --output OUTPUT
                        Path to output CSV file (default
                        "./sample_output.csv")
```

## Usage

#### Docker container

- As explained in [Quickstart](#quick-start)

#### From Terminal

`python3 -m fwfparser <args>`

#### As a module

`pip3 install .`

`python3`

```
from fwfparser import fwf

#parse given fwf using given specs to csv with a given delimiter
data = fwf.read_fwf(spec='./example/spec.json', fwf_path='./example/fwf.txt')

#convert given fwf using given specs to csv with a given delimiter
fwf.fwf_to_csv(spec='./example/spec.json', fwf_path='./example/fwf.txt', csv_path='./example/my_output.csv, sep='\t')

# generate a random fwf file of given length using the given specs, in the given path
fwf.generate_fwf_file(spec_path='./example/spec.json', fwf_path='./example/my_generated_fwf.txt', length=1000)
```

## CI

Uses pre-commit hooks, github actions.
Refer to:

1. [pre-commit-hooks](.pre-commit-config.yaml)
2. [Github actions workflow](./.github/workflows/push.yml)
   1. [Tests](tests/) are run in the github workflow and
   2. if successful, docker images are built and pushed to my dockerhub

## Repo

Repo structure is:

```

•••• tree
.
├── Dockerfile
├── LICENSE
├── MANIFEST.in
├── Makefile
├── Pipfile
├── Pipfile.lock
├── README.md
├── VERSION
├── example
│ ├── fwf.txt
│ ├── fwf_noencode.txt
│ ├── fwf_parsed.csv
│ ├── fwf_parsed_noencode.csv
│ └── spec.json
├── fwfparser
│ ├── **init**.py
│ ├── **main**.py
│ ├── **pycache**
│ │ ├── **init**.cpython-37.pyc
│ │ ├── **main**.cpython-37.pyc
│ │ ├── fwf.cpython-37.pyc
│ │ ├── supported_specs.cpython-37.pyc
│ │ └── utils.cpython-37.pyc
│ ├── fwf.py
│ └── utils.py
├── generate_parse_files.sh
├── pytest.ini
├── setup.py
├── specs
│ ├── HowWeWork.md
│ ├── JobAd.md
│ ├── README.md
│ └── spec.json
├── test_fwfparser.sh
└── tests
├── **init**.py
├── **pycache**
│ ├── **init**.cpython-37.pyc
│ └── test_fwf.cpython-37-pytest-5.2.2.pyc
├── test_csv_valid.csv
├── test_csv_valid_nln.csv
├── test_fwf.py
├── test_fwf_valid.txt
├── test_spec_invalid_json.json
├── test_spec_invalid_minimum.json
└── test_spec_valid.json

```
