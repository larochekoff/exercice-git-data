from main import saluer


def test_saluer() -> None:
    assert saluer("World") == "Bonjour, World"
