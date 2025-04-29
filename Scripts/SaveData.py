import csv

# Create the headers based on the header_value_mapping
Foreign_ETF_headers = [
    '(ファイル名)', '国内約定年月日', '国内受渡年月日', '現地約定年月日', '現地受渡年月日', '銘柄コード', '銘柄名', '市場', '口座区分',
    '自己・委託', '為替レート', '売買', '決済方法', '取引通貨', '約定数量', '約定価格', '約定金額', '現地手数料等', '受渡金額', '消費税',
    '国内手数料', '円貨 (現地精算金額)', '外貨 (現地精算金額)', '取引の種類'
]

Japan_ETF_headers = [
    '(ファイル名)', '約定日', 'ご精算日', '銘柄名', '数量', '単価', '約定金額', '銘柄コード', '取引区分', 'ご精算金額',
    '市場', '取引', '受渡条件', '特定区分', '譲渡益税区分' # Note! The last 5 on this row: First 3 always appear, but the last 2 are varied
]

# Step 5: Save extracted data to CSV
def commit(extracted_data, output_file_path):
    try:
        if not extracted_data:
            print("No data to save.")
            return

        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Before writing, check what file pattern we have
            print(extracted_data)
            exit()

            # Write the headers first
            csv_writer.writerow(Foreign_ETF_headers)

            # Write each trade's data as a row
            for extracted_text in extracted_data:
                for line in extracted_text:
                    if isinstance(line, list):  # If it's a list of values
                        csv_writer.writerow(line)  # Write each row of values
                    else:
                        csv_writer.writerow([line])  # In case it is a stray string

    except Exception as e:
        print(f"Error saving to CSV: {e}")