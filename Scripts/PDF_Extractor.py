import os
import csv
import pymupdf

# Folders
parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
pdf_folder = os.path.join(parent_folder, 'PDF')
output_folder = os.path.join(parent_folder, 'Output (CSV)')
output_file_path = os.path.join(output_folder, "Output.csv")

## Foreign ETF markers to know where data starts/ends
Foreign_ETF_start_marker = "お問合せ先："
Foreign_ETF_end_marker = "＊＊   以 　 上   ＊＊"

## Japan ETF markets to know where data starts/ends
Japan_ETF_start_marker = "取引店"
Japan_ETF_end_marker = "◎投資信託は元金や利回りが保証されているものではありません。"

# Pattern 4a) Foreign ETF <Header, Value> row index mapping
# The reason is that data is extracted in an inconsistent order, hence the need to map it. The mapping also helps in case the order changes in the future.
header_value_mapping = {
    0: 13,  # 国内約定年月日 (Header)
    1: 15,  # 国内受渡年月日 (Header)
    2: 14,  # 現地約定年月日 (Header)
    3: 16,  # 現地受渡年月日 (Header)
    4: 17,  # 銘柄コード (Header)
    5: 18,  # 銘　柄　名 (Header)
    6: 25,   # 市場 (Header)
    7: 26,   # 口座区分 (Header)
    8: 23,   # 自己・委託 (Header)
    9: 24,   # 為替レート (Header)
    10: 21,  # 売買 (Header)
    11: 22,  # 決済方法 (Header)
    12: 20,  # 取引通貨 (Header)
    27: 36,  # 約定数量 (Header)
    28: 37,  # 約定価格 (Header)
    29: 38,  # 約定金額 (Header)
    30: 39,  # 現地手数料等 (Header)
    31: 44,  # 受渡金額 (Header)
    32: 43,  # 消費税 (Header)
    33: 42,  # 国内手数料
    34: 40,  # 円貨 (現地精算金額)
    35: 41,  # 外貨 (現地精算金額)
    45: 19,  # 取引の種類 (Header)
}

# Pattern 4b) Japan ETF <Header, Value> row index mapping
# The reason is that data is extracted in an inconsistent order, hence the need to map it. The mapping also helps in case the order changes in the future.
# <TBD>

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



# Step 3: Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    try:
        pdf_document = pymupdf.open(pdf_path)
        full_text = []

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text") # Read page text

            filtered_text = []
            lines = page_text.split("\n")

            # Check if the file is Foreign ETF or Japan ETF file
            if "投資信託　取引報告書" == lines[1].strip():
                filtered_text = parse_text_from_japan_etf(lines)
            elif "外国株式等 取引報告書" == lines[2].strip():
                filtered_text = parse_text_from_foreign_etf(lines)
            else:
                print("Error: Unknown data format.")
                exit(1)

            print("Filtered", filtered_text)
            print("Filtered length", len(filtered_text))

            # Process data in chunks of 46 items
            for i in range(0, len(filtered_text), 46):
                # Grab a chunk of 46 items (or the remaining items if less than 46)
                chunk = filtered_text[i:i + 46]

                # Initialize an empty list to hold the mapped data for this chunk
                mapped_text = []

                # Add PDF name on the first row
                mapped_text.append(os.path.basename(pdf_document.name))

                # Iterate over the header_value_mapping and extract corresponding values
                for header, value in header_value_mapping.items():
                    # Make sure the index exists within the chunk
                    if header < len(chunk) and value < len(chunk):
                        val = f"{chunk[value]}".replace(",", ".")
                        #print("Val",val)
                        mapped_text.append(val)

                # Add mapped_text as a new row in full_text for this chunk
                print("Appending mapped_text", mapped_text)
                full_text.append(",".join(mapped_text))  # Join all the values in mapped_text with commas

        return full_text

    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return []


# Step 4: Pattern 1) Parse Japan ETF files
def parse_text_from_japan_etf(lines):
    trade_count = 0
    line_count = 0
    filtered_lines = []

    # First data is in row 6 initially, or when we run into 3 digit, 6 digit and 3 digit like value (Example:３３２　　　　　１３７０７３　　　０３０)
    # End of file is when
    for line in lines:
        print("Japan", line.strip())

    return filtered_lines


# Step 4: Pattern 2) Parse Japan ETF files
# Function to parse Foreign ETF files
def parse_text_from_foreign_etf(lines):
    trade_count = 0
    line_count = 0
    filtered_lines = []
    start_marker_found = False

    for line in lines:
        if not start_marker_found:
            if Foreign_ETF_start_marker in line:
                start_marker_found = True
            continue

        if Foreign_ETF_end_marker in line:
            break
        if "備考" in line:
            continue
        if "約定数量" in line and line_count == 26:
            filtered_lines.append("(Empty Field: 口座区分)")
            line_count += 1
        if "国内約定年月日国内受渡年月日" in line:
            filtered_lines.extend(["国内約定年月日", "国内受渡年月日"])
            line_count += 2
        elif "現地約定年月日現地受渡年月日" in line:
            filtered_lines.extend(["現地約定年月日", "現地受渡年月日"])
            line_count += 2
        elif "銘　柄　名" in line:
            filtered_lines.append("銘柄名")
            line_count += 1
        elif "現地精算金額" in line:
            continue
        elif "外貨" in line and "決済" not in line:
            filtered_lines.append("外貨 (現地精算金額)")
            line_count += 1
        elif "円貨" in line and "決済" not in line:
            filtered_lines.append("円貨 (現地精算金額)")
            line_count += 1
        elif "円貨決済" == line:
            filtered_lines.append(line)
            line_count += 1
        elif "取引の種類" in line:
            filtered_lines.append(line)
            trade_count += 1
            line_count += 1
        else:
            if start_marker_found and line:
                filtered_lines.append(line.strip())
                line_count += 1
    return filtered_lines



# Step 5: Save extracted data to CSV
def save_to_csv(extracted_data, output_filename="Output.csv"):
    try:
        if not extracted_data:
            print("No data to save.")
            return

        # Create the headers based on the header_value_mapping
        headers = [
            '(ファイル名)','国内約定年月日', '国内受渡年月日', '現地約定年月日', '現地受渡年月日', '銘柄コード', '銘柄名', '市場', '口座区分',
            '自己・委託', '為替レート', '売買', '決済方法', '取引通貨', '約定数量', '約定価格', '約定金額', '現地手数料等',
            '受渡金額', '消費税', '国内手数料', '円貨 (現地精算金額)', '外貨 (現地精算金額)', '取引の種類'
        ]

        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write the headers first
            csv_writer.writerow(headers)

            # Write each trade's data as a row
            for extracted_text in extracted_data:
                for line in extracted_text:
                    if isinstance(line, list):  # If it's a list of values
                        csv_writer.writerow(line)  # Write each row of values
                    else:
                        csv_writer.writerow([line])  # In case it is a stray string

        print(f"Data saved to {output_filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


# --------------------------------------------------------------------------------------------- #

# Step 1: Main execution
if __name__ == '__main__':
    try:
        # Extract text from all PDFs in the current directory
        extracted_data = extract_text_from_all_pdfs()

        # Save the extracted data to a CSV file
        save_to_csv(extracted_data)
        print("Extraction complete!")
    except Exception as e:
        print(f"Error during execution: {e}")