# import random
from .utils import parse_spec_file


class DataFrameF:
    """DataFrame to store Class
    """

    def __init__(self, spec=None):
        if spec is None:
            self.columns = []
            self.rows = []
        else:
            self.specs = parse_spec_file(spec)
        return

    def _read_fwf(self):
        return self


def read_fwf(spec, *args, **kwargs):
    return DataFrameF(spec)._read_fwf()
