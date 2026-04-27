import pytest
from rror import Mirror
from src.main import main


class TestMain:
    def test_main_runs(self, capsys):
        main()

        captured = capsys.readouterr()
        assert "Hello from this project." in captured.out


if __name__ == "__main__":

    raise SystemExit(pytest.main([__file__]))
