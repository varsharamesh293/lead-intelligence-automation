import pandas as pd

def clean_csv(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Cleans a CSV with broken quotes and returns a pandas DataFrame.
    """
    # Read raw lines
    with open(input_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Fix header and double quotes
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]  
        line = line.replace('""', '"')
        cleaned_lines.append(line + "\n")

    # Write cleaned CSV temporarily
    temp_path = output_path
    with open(temp_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    # Load with pandas
    df = pd.read_csv(temp_path)
    return df
