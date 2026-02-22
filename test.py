def main():
    delta_pairs = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    for pair in delta_pairs:
        print(pair)

if __name__ == "__main__":
    main()
