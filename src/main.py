from lexer.lexer import Lexer
import os

def run_test_case(file_path, output_file):
    with open(file_path, "r") as f:
        code = f.read()

    lexer = Lexer()
    tokens = lexer.tokenize(code)

    output_lines = []
    output_lines.append(f"\n=== TOKENS from {os.path.basename(file_path)} ===")
    for token in tokens:
        line = f"{token['type']:<10} : {token['value']}"
        output_lines.append(line)
    output_lines.append(f"\nTotal tokens: {len(tokens)}")
    
    # Print to console
    for line in output_lines:
        print(line)
    
    # Write to file
    output_file.write("\n".join(output_lines) + "\n\n")

def main():
    samples_dir = "tests/samples"
    output_dir = "tests/output"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    test_files = [f for f in os.listdir(samples_dir) if f.endswith(".lol")]

    if not test_files:
        print("No .lol test cases found in tests/samples/")
        return

    # Open output file for writing output
    output_path = os.path.join(output_dir, "token_output.txt")
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("LOLCODE Lexer Token Output\n")
        output_file.write("=" * 60 + "\n\n")
        
        for file in test_files:
            file_path = os.path.join(samples_dir, file)
            run_test_case(file_path, output_file)
    
    print(f"\n Output written to: {output_path}")

if __name__ == "__main__":
    main()
