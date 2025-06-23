import shutil

import pytest

from transonic.testing import path_data_tests


@pytest.fixture
def path_input_files(tmp_path):
    self = tmp_path / "input_files"
    self.mkdir()
    for path in path_data_tests.glob("*.py"):
        shutil.copy(path, self)
    return self
