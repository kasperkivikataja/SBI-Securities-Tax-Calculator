"""
    Developer: Kasper Kivikataja
    Date: May 1st, 2025
    Purpose: Calls PDF readers to parse data. Once parsing is done, calls SaveData class when it receives parsed data.
"""

import os
import pymupdf
import SaveData
import Scripts.ParsePatterns.Foreign_ETF
import Scripts.ParsePatterns.Japan_ETF

# Folders
parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
pdf_folder = os.path.join(parent_folder, 'PDF')
output_file_path = os.path.join(parent_folder, 'Output')

# --------------------------------------------------------------------------------------------- #

# Step 3: Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    try:
        pdf_document = pymupdf.open(pdf_path)
        pdf_name = os.path.basename(pdf_path)

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text")
            lines = page_text.split("\n")

            # Determine the format
            if "投資信託　取引報告書" == lines[1].strip():
                parsed_values = Scripts.ParsePatterns.Japan_ETF.parse_values_from_japan_etf(lines, pdf_name)
                return {"pdf": pdf_name, "format": "Japan", "values": parsed_values}

            elif "外国株式等 取引報告書" == lines[2].strip():
                parsed_values = Scripts.ParsePatterns.Foreign_ETF.parse_values_from_foreign_etf(lines, pdf_name)
                return {"pdf": pdf_name, "format": "Foreign", "values": parsed_values}

            else:
                print(f"Unknown format in {pdf_name}")
                exit()
        return None

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return {"pdf": os.path.basename(pdf_path), "format": "Error", "values": []}

# Step 2: Extract text from all PDFs in the current directory
def extract_text_from_all_pdfs():
    try:
        files = os.listdir(pdf_folder)
        pdf_files = [file for file in files if file.lower().endswith('.pdf')]

        if not pdf_files:
            print("No PDF files found in the directory.")

        extracted_data = {}

        pdf_count = 0;
        for pdf_file in pdf_files:
            pdf_count += 1;
            print(f"Extracting text from {pdf_file}... ({pdf_count}/{len(pdf_files)})")
            pdf_path = os.path.join(pdf_folder, pdf_file)
            result = extract_text_from_pdf(pdf_path)

            if result.get("values"):  # Safely check for "values"
                extracted_data[pdf_file] = result  # Use filename as key

        return extracted_data

    except Exception as e:
        print(f"Error processing PDFs: {e}")
        return {}


# --------------------------------------------------------------------------------------------- #

# Step 1: Main execution
if __name__ == '__main__':
    try:
        # Extract text from all PDFs in the current directory
        extracted_data = extract_text_from_all_pdfs()

        # Save the extracted data to a CSV file
        SaveData.commit(extracted_data, output_file_path)

        #print("Extraction complete!")
    except Exception as e:
        print(f"Error during execution: {e}")