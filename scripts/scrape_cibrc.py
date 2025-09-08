import requests
import pdfplumber
import pandas as pd
import os

PDF_URL = "https://ppqs.gov.in/sites/default/files/major_uses_of_pesticides_insecticides_as_on_31.03.2024.pdf"
PDF_PATH = "cibrc_pesticides.pdf"
CSV_PATH = "cibrc_data.csv"

def download_pdf(url, path):
    """Downloads a PDF from a given URL."""
    if os.path.exists(path):
        print(f"✅ PDF '{path}' already exists. Skipping download.")
        return True
    try:
        print(f"--- 📥 Downloading PDF from {url} ---")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ PDF downloaded successfully to '{path}'.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download PDF: {e}")
        return False

def parse_pdf_to_csv(pdf_path, csv_path):
    """
    Parses the downloaded PDF with more robust logic to handle
    tables with varying column counts.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found at '{pdf_path}'. Cannot parse.")
        return

    print(f"--- 📖 Parsing data from '{pdf_path}' ---")
    all_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"  -> Processing page {i+1}/{len(pdf.pages)}...")
                tables = page.extract_tables()
                for table in tables:
                    # Skip header rows
                    for row in table[1:]:
                        # Clean the row of None values and newlines
                        cleaned_row = [str(cell).replace('\n', ' ') if cell is not None else '' for cell in row]
                        all_data.append(cleaned_row)
        
        if not all_data:
            print("❌ No tables were extracted from the PDF.")
            return

        # --- THIS IS THE FIX ---
        # Create a DataFrame without specifying columns first, to handle varying lengths.
        df = pd.DataFrame(all_data)

        # We assume the first 5 columns are the most important ones.
        # This is a robust way to handle tables with extra, inconsistent columns.
        num_columns = df.shape[1]
        if num_columns < 4:
            print(f"❌ Aborting: Found tables with fewer than 4 columns. Check PDF structure.")
            return
            
        # Select the first 4 or 5 columns which typically contain the key info
        # This avoids errors if some tables have more columns
        col_count_to_use = min(5, num_columns)
        df = df.iloc[:, :col_count_to_use]

        # Assign column names based on the expected structure
        column_names = ['S_No', 'Insecticide', 'Pest', 'Crop', 'Dosage']
        df.columns = column_names[:col_count_to_use]

        # Select and rename the final columns we need
        df = df[['Insecticide', 'Pest', 'Crop', 'Dosage']]
        df.columns = ['chemical_name', 'pest_name', 'crop_name', 'dosage']

        # Final data cleaning
        df = df.dropna(subset=['pest_name', 'crop_name'])
        df = df[df['pest_name'].str.strip() != '']
        df = df[df['crop_name'].str.strip() != '']

        df.to_csv(csv_path, index=False)
        print(f"✅ Data successfully parsed and saved to '{csv_path}'. Found {len(df)} records.")

    except Exception as e:
        print(f"❌ An error occurred during PDF parsing: {e}")

if __name__ == "__main__":
    if download_pdf(PDF_URL, PDF_PATH):
        parse_pdf_to_csv(PDF_PATH, CSV_PATH)