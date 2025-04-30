import os
import re
import pymupdf
import SaveData
import Scripts.ParsePatterns.Foreign_ETF
import Scripts.ParsePatterns.Japan_ETF

# Folders
parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
pdf_folder = os.path.join(parent_folder, 'PDF')
output_file_path = os.path.join(parent_folder, 'Output/Output.csv')

# Step 4: Parse & Map data (Foreign ETF pattern)
def map_text_from_foreign_etf(filtered_text, pdf_document_name):

    print("AA", filtered_text)

    # Process data in chunks of 46 items
    for i in range(0, len(filtered_text), Scripts.ParsePatterns.Foreign_ETF.Foreign_ETF_chunk_size):
        # Grab a chunk of 46 items (or the remaining items if less than 46)
        chunk = filtered_text[i:i + Scripts.ParsePatterns.Foreign_ETF.Foreign_ETF_chunk_size]

        # Initialize an empty list to hold the mapped data for this chunk
        mapped_text = []

        # Add PDF name on the first row
        mapped_text.append(pdf_document_name)

        # Iterate over the header_value_mapping and extract corresponding values
        for header, value in Scripts.ParsePatterns.Foreign_ETF.foreignETF_header_value_mapping.items():
            # Make sure the index exists within the chunk
            if header < len(chunk) and value < len(chunk):
                val = f"{chunk[value]}".replace(",", ".") # Do we need to do this here again...
                mapped_text.append(val)

        # Add mapped_text as a new row in full_text for this chunk
        mapped_text.append(",".join(mapped_text))  # Join all the values in mapped_text with commas

    return mapped_text

# Step 4: Parse & Map data (Japan ETF pattern)
def map_text_from_japan_etf(filtered_text, pdf_document_name):

    print(filtered_text)
    exit()
    # Initialize an empty list to hold the mapped data for this chunk
    mapped_text = []

    # Add PDF name on the first row
    mapped_text.append(pdf_document_name)

    # Regex pattern for matching full-width or half-width date-like entries
    date_pattern = re.compile(r'[\d０-９]{4}/[\d０-９]{1,2}/[\d０-９]{1,2}')

    records = []
    current_record = []

    for item in filtered_text:
        if date_pattern.match(item) and current_record:
            records.append(current_record)
            current_record = []
        current_record.append(item)

    # Append the last record
    if current_record:
        records.append(current_record)

    # Print nicely
    for i, record in enumerate(records, 1):
        print(f"Record {i}:")
        for field in record:
            print(" ", field)

# --------------------------------------------------------------------------------------------- #

# Step 3: Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    try:
        pdf_document = pymupdf.open(pdf_path)
        full_text = []

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text")  # Read page text
            pdf_name = os.path.basename(pdf_path)

            filtered_text = []
            lines = page_text.split("\n")

            # Check if the file is Foreign ETF or Japan ETF file
            if "投資信託　取引報告書" == lines[1].strip():
                filtered_text = Scripts.ParsePatterns.Japan_ETF.parse_text_from_japan_etf(lines)  # Step 1: Parse and clean up (Japan ETF)
                full_text = map_text_from_japan_etf(filtered_text, pdf_name)  # Step 2: Map data for CSV (Japan ETF)

            elif "外国株式等 取引報告書" == lines[2].strip():
                filtered_text = Scripts.ParsePatterns.Foreign_ETF.parse_text_from_foreign_etf(lines)  # Step 1: Parse and clean up (Foregn ETF)
                full_text = map_text_from_foreign_etf(filtered_text, pdf_name)  # Step 2: Map data for CSV (Foregn ETF)

            else:
                print("Error: Unknown data format.")
                exit(1)

        return full_text

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return []

# Step 2: Extract text from all PDFs in the current directory
def extract_text_from_all_pdfs():
    try:
        files = os.listdir(pdf_folder)
        pdf_files = [file for file in files if file.lower().endswith('.pdf')]

        if not pdf_files:
            print("No PDF files found in the directory.")

        extracted_data = []

        # Process each PDF file
        for pdf_file in pdf_files:
            print(f"Extracting text from {pdf_file}...")
            pdf_path = os.path.join(pdf_folder, pdf_file)
            text = extract_text_from_pdf(pdf_path)

            if text:  # Only append if text was extracted
                extracted_data.append(text)

        return extracted_data
    except Exception as e:
        print(f"Error processing PDFs: {e}")
        return []

# --------------------------------------------------------------------------------------------- #

# Step 1: Main execution
if __name__ == '__main__':
    try:
        # Extract text from all PDFs in the current directory
        extracted_data = extract_text_from_all_pdfs()

        # Save the extracted data to a CSV file
        SaveData.commit(extracted_data, output_file_path)

        print("Extraction complete!")
    except Exception as e:
        print(f"Error during execution: {e}")