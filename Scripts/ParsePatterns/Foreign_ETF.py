"""
    Developer: Kasper Kivikataja
    Date: May 1st, 2025
    Purpose: Parses Foreign ETF PDF formatting and cleans it up for saving
"""

from operator import index
import Scripts

Foreign_ETF_start_marker = "取引通貨"
Foreign_ETF_end_marker = "**   以   上   **"
Foreign_ETF_expected_value_count = 24 # 23 values + PDF name in the end

# Headers used by SaveData to
Foreign_ETF_headers = [
    "国内約定年月日", "国内受渡年月日", "現地約定年月日", "現地受渡年月日", "銘柄コード", "銘柄名", "取引の種類", "取引通貨", "売買", "決済方法",
    "自己・委託", "為替レート", "市場", "口座区分", "約定数量", "約定価格", "約定金額", "現地手数料等", "外貨 (現地精算金額)", "円貨 (現地精算金額)", "国内手数料",
    "消費税", "受渡金額"
]

# A helper list to help us skip lines
Foreign_ETF_unwanted_headers = [
    "備考", "現地精算金額", "国内約定年月日国内受渡年月日", "現地約定年月日現地受渡年月日", "銘 柄 名", "円貨", "外貨"
]

# INTs (amounts which we want to call clean_integer to remove all dots and commas)
Foreign_ETF_clean_integer_indexes = [
    17, 19, 20, 23
]

# --------------------------------------------------------------------------------------------- #

def parse_values_from_foreign_etf(lines, pdf_name):
    final_values = []
    startmarker_found = False   # Each PDF has a static markers where we can start parsing data from
    endmarker_found = False     # Each PDF has a static markers where we can end parsing
    trade_count = 1              # Number of trades within a page

    for line in lines:
        line = Scripts.StringHelper.clean_line_strip_and_unicode_normalize(line)

        if not startmarker_found:
            if Foreign_ETF_start_marker in line:
                startmarker_found = True
                final_values.append(pdf_name)
                continue
            else:
                continue

        if not endmarker_found:
            if Scripts.StringHelper.is_date(line):
                missing_Kubun_And_PDF_name = len(final_values) is trade_count * 23 # We know we have reached then end when the count divided by 23 or 24

                if missing_Kubun_And_PDF_name:
                    final_values = add_empty_fields(trade_count, final_values)
                    final_values.insert(len(final_values), pdf_name)
                    trade_count += 1

            elif Foreign_ETF_end_marker in line:
                missing_Kubun_And_PDF_name = len(final_values) is trade_count * 23  # We know we have reached then end when the count divided by 23 or 24
                if missing_Kubun_And_PDF_name:
                    final_values = add_empty_fields(trade_count, final_values)
                break
            else:
                if line in Foreign_ETF_headers:
                    continue

                elif line in Foreign_ETF_unwanted_headers:
                    continue

        final_values.append(line)

    # Clean Indexes from dots case-by-case. These are cleaned based on "Foreign_ETF_clean_integer_indexes"
    final_values = clean_final_values(final_values)

    return final_values


# --------------------------------------------------------------------------------------------- #

def clean_final_values(final_values):
    for i in range(0, len(final_values), Foreign_ETF_expected_value_count):  # Process in chunks
        chunk = final_values[i:i + Foreign_ETF_expected_value_count]

        for j, value in enumerate(chunk):
            if j in Foreign_ETF_clean_integer_indexes:
                chunk[j] = Scripts.StringHelper.replace_dots_with_empty(value)

        # Replace the cleaned chunk back into the original list
        final_values[i:i + Foreign_ETF_expected_value_count] = chunk

    return final_values

def add_empty_fields(tradeCount, final_values):
    insert_index = 14 * tradeCount
    final_values.insert(insert_index, "Empty (区分)")
    return final_values