from rror import Mirror
from __PACKAGE_NAME__ import __name__ as package_name


class TestPackage:
    def test_package_imports(self):
        assert package_name == "__PACKAGE_NAME__"
