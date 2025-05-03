"""
    Developer: Kasper Kivikataja
    Date: May 1st, 2025
    Purpose: Parses Foreign ETF PDF formatting and cleans it up for saving
"""

from operator import index
import Scripts

Foreign_ETF_start_marker = "お問合せ先:"
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
    17, 18, 19, 20, 21, 22, 23
]

# --------------------------------------------------------------------------------------------- #

def parse_values_from_foreign_etf(lines, pdf_name):
    final_values = parse(lines, pdf_name)
    final_values = remove_dots_from_integers(final_values);
    return final_values

# --------------------------------------------------------------------------------------------- #

def parse(lines, pdf_name):
    new_lines = []
    start_found = False
    row = 0
    trade_count = 0

    for i in range(len(lines)):
        line = Scripts.StringHelper.clean_line_strip_and_unicode_normalize(lines[i])

        if not start_found:
            if Foreign_ETF_start_marker in line:
                start_found = True
                continue
            else:
                continue

        # Skip adding any headers
        if line in Foreign_ETF_headers or line in Foreign_ETF_unwanted_headers:
            continue

        elif Foreign_ETF_end_marker in line:
            break

        if row == (trade_count * Foreign_ETF_expected_value_count):
            new_lines.append(pdf_name)
            row += 1
            trade_count += 1

        new_lines.append(line)
        row += 1

        # Check Kubun
        if row == trade_count * Foreign_ETF_expected_value_count - 10:
            if i + 1 < len(lines):
                next_line = Scripts.StringHelper.clean_line_strip_and_unicode_normalize(lines[i + 1])
                if "数量" in next_line:
                    new_lines.append("Empty (区分)")
                    row += 1
    return new_lines


def remove_dots_from_integers(final_values):
    for i in range(0, len(final_values), Foreign_ETF_expected_value_count):
        chunk = final_values[i:i + Foreign_ETF_expected_value_count]

        for idx in Foreign_ETF_clean_integer_indexes:
            if idx < len(chunk):
                chunk[idx] = Scripts.StringHelper.replace_dots_with_empty(chunk[idx])

        # Replace the chunk in the original list
        final_values[i:i + Foreign_ETF_expected_value_count] = chunk

    return final_values



def add_empty_fields(tradeCount, final_values):
    insert_index = 14 * tradeCount
    final_values.insert(insert_index, "Empty (区分)")
    return final_values