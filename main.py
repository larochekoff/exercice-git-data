# correction ruff
def saluer(nom: str) -> str:
    """Retourne un message de salutation."""
    return f"Bonjour, {nom}"


if __name__ == "__main__":
    print(saluer("World"))
