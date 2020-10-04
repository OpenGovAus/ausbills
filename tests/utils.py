from pathlib import Path


def read_data(name):
    with open(Path(__file__).parent / "data" / name, 'r') as f:
        return f.read()
