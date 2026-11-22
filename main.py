from pathlib import Path


def main():
    src = Path(__file__).parent / "entry.png"
    dst = Path("/output/entry.png")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())


if __name__ == "__main__":
    main()
