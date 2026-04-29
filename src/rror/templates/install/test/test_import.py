import pytest
from rror import Mirror
from __PACKAGE_NAME__ import __name__ as package_name


class TestPackage:
    def test_package_imports(self):
        assert package_name == "__PACKAGE_NAME__"


if __name__ == "__main__":
    raise SystemExit(pytest.main(['-v',
                                  __file__,
                                  #  '--tb=short',
                                  '--color=yes',
                                  #  "-k test_package_imports",
                                  ]))
