import pytest
from fwfparser.fwf import fwf


def test_no_spec_file_exception():
    """Test that an exception is raised when no path to spec file is not given
    """
    with pytest.raises(TypeError) as error:
        assert fwf()
    assert (
        str(error.value) == "__init__() missing 1 required positional argument: 'spec'"
    )
