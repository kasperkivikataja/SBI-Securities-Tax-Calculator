"""
    Developer: Kasper Kivikataja
    Date: May 1st, 2025
    Purpose: Saves parsed PDF data into CSVs. Each pattern (e.g., foreign ETFs, Japan ETFs) are saved into
    their respective files
"""

import csv
import Scripts
import os

# Helper function to chunk the list into smaller chunks of a specified size
def chunk_list(data, size):
    return [data[i:i+size] for i in range(0, len(data), size)]

def commit(extracted_data, output_folder):
    try:
        if not extracted_data:
            print("No data to save.")
            return

        foreign_rows = []
        japan_rows = []

        # Loop through the extracted data and process each item
        for item in extracted_data.values():
            file_format = item.get("format")
            values = item.get("values", [])

            # Process Foreign format
            if file_format == "Foreign":
                #print("Processing Foreign format...")
                # Chunk the values into rows of 23 items each
                foreign_rows.extend(chunk_list(values, Scripts.ParsePatterns.Foreign_ETF.Foreign_ETF_expected_value_count))

            # Process Japan format
            elif file_format == "Japan":
                #print("Processing Japan format...")
                # Chunk the values into rows of ? items each
                japan_rows.extend(chunk_list(values, Scripts.ParsePatterns.Japan_ETF.Japan_ETF_expected_value_count))

        # Helper function to write data to CSV
        def write_csv(path, headers, rows):
            headers_with_pdf_name = headers
            headers_with_pdf_name.insert(0, "File")

            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers_with_pdf_name)
                writer.writerows(rows)

        # Write Foreign ETF CSV if there are rows to write
        if foreign_rows:
            japanese = Scripts.ParsePatterns.Foreign_ETF.Foreign_ETF_headers
            english = Scripts.ParsePatterns.Foreign_ETF.Foreign_ETF_headers_English

            combined_headers = [f"{jp} ({en})" for jp, en in zip(japanese, english)]

            write_csv(
                os.path.join(output_folder, "foreign_etf_output.csv"),
                combined_headers,
                foreign_rows
            )

        # Write Japan ETF CSV if there are rows to write
        if japan_rows:
            japanese = Scripts.ParsePatterns.Japan_ETF.Japan_ETF_headers
            english = Scripts.ParsePatterns.Japan_ETF.Japan_ETF_headers_English

            combined_headers = [f"{jp} ({en})" for jp, en in zip(japanese, english)]

            write_csv(
                os.path.join(output_folder, "japan_etf_output.csv"),
                combined_headers,
                japan_rows
            )

        #print("Data saved to CSV files successfully.")

    except Exception as e:
        print(f"Error saving to CSV: {e}")

