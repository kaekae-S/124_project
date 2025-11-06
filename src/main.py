from lexer.lexer import Lexer
import os

def run_test_case(file_path):
    with open(file_path, "r") as f:
        code = f.read()

    lexer = Lexer()
    tokens = lexer.tokenize(code)

    print(f"\n=== TOKENS from {os.path.basename(file_path)} ===")
    for token in tokens:
        print(f"{token['type']:<10} : {token['value']}")
    print("\nTotal tokens:", len(tokens))

def main():
    samples_dir = "tests/samples"
    test_files = [f for f in os.listdir(samples_dir) if f.endswith(".lol")]

    if not test_files:
        print("No .lol test cases found in tests/samples/")
        return

    for file in test_files:
        run_test_case(os.path.join(samples_dir, file))

if __name__ == "__main__":
    main()
