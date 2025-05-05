"""
    Developer: Kasper Kivikataja
    Date: May 1st, 2025
    Purpose: Parses Japan ETF PDF formatting and cleans it up for saving
"""

from Scripts import StringHelper
import re

## Japan ETF markets to know where data starts/ends
Japan_ETF_startIndex = 6
Japan_ETF_end_marker1 = "◎投資信託は元金や利回りが保証されているものではありません。"
Japan_ETF_end_marker2 = "以下余白"
Japan_ETF_expected_value_count = 15 # 14 + 1 values + PDF name in the end

Japan_ETF_headers = [
    "約定日", "ご精算日", "銘柄名", "数量", "単価", "約定金額", "銘柄コード", "取引区分", "ご精算金額",
    # Note 1: "市場", "取引", "受渡条件" are in all files
    # Note 2: "特定区分", "譲渡益税区分" can change depending on file
    "市場", "取引", "受渡条件", "(特定)区分", "譲渡益税区分"
]

Japan_ETF_headers_English = [
  "Contract Date", "Settlement Date", "Name", "Quantity", "Unit Price", "Contract Amount", "Ticker", "Transaction Type", "Settlement Amount",
  "Market", "Transaction", "Settlement Condition", "Account Classification", "Capital Gains Tax Type"
];

Japan_ETF_known_keys = ['市場', '取引', '受渡条件', '特定区分', '譲渡益税区分']
Japan_ETF_extra_keywords = ['NISA成長投資枠']  # Standalone labels that can appear after values
Japan_ETF_required_keys = {'市場', '取引', '受渡条件'}

# --------------------------------------------------------------------------------------------- #

def parse_values_from_japan_etf(lines, pdf_name):
    final_values = []
    trade_count = 0
    index = 0

    for line in lines[Japan_ETF_startIndex:]:
        line = StringHelper.clean_line_strip_and_unicode_normalize(line)

        if line.startswith("市場"):
            addedValues = add_trade_data(lines, index)
            final_values.extend(addedValues)
            insert_index = trade_count * Japan_ETF_expected_value_count
            trade_count += 1
            add_pdf_and_dates(final_values, insert_index, pdf_name, lines[Japan_ETF_startIndex], lines[Japan_ETF_startIndex + 1])

        elif Japan_ETF_end_marker1 in line or Japan_ETF_end_marker2 in line:
            break
        index += 1
    return final_values

# --------------------------------------------------------------------------------------------- #

def add_trade_data(lines, index):
    final_values = []

    # 2. Combine index 8 and 9 as they are part of 銘柄名
    value1 = StringHelper.clean_line_strip_and_unicode_normalize(lines[index])
    value2 = StringHelper.clean_line_strip_and_unicode_normalize(lines[index + 1])
    final_values.append(value1 + value2)

    # 3. Separate three integers
    values = lines[index + 2].split()
    if len(values) == 3:
        for value in values:
            value = StringHelper.clean_line_strip_and_unicode_normalize(value)
            value = StringHelper.replace_commas_with_empty(value)
            value = StringHelper.replace_dots_with_empty(value)
            final_values.append(value)

    # 4. Clean 銘柄コード parenthesis and empty spaces
    ticker = StringHelper.clean_line_strip_and_unicode_normalize(lines[index + 3])
    ticker = StringHelper.clean_line_parenthesis(ticker)
    final_values.append(ticker)

    # 5. Add buy/sell
    final_values.append(StringHelper.clean_line_strip_and_unicode_normalize(lines[index + 4]))

    # 6. Add Buy/Sell Price
    value = StringHelper.clean_line_strip_and_unicode_normalize(lines[index + 5])
    value = StringHelper.replace_commas_with_empty(value)
    value = StringHelper.replace_dots_with_empty(value)
    final_values.append(value)

    # 7. Clean ['市場', '取引', '受渡条件', '特定区分', '譲渡益税区分']
    market_data = StringHelper.clean_line_strip_and_unicode_normalize(lines[index + 6])
    market_data = clean_market_data(market_data)
    final_values.extend(market_data)

    return final_values

# --------------------------------------------------------------------------------------------- #

def add_pdf_and_dates(final_values, index, pdf_name, date1, date2):
    final_values.insert(index, pdf_name)
    final_values.insert(index + 1, StringHelper.clean_line_date_string(StringHelper.clean_line_strip_and_unicode_normalize(date1)))  # 約定日
    final_values.insert(index + 2, StringHelper.clean_line_date_string(StringHelper.clean_line_strip_and_unicode_normalize(date2)))  # ご精算日

def clean_market_data(line):
    #print("Market Data Before:", line)

    # Step 1: Extract NISA-related keyword if present
    nisa_value = ""
    for keyword in Japan_ETF_extra_keywords:
        if keyword in line:
            idx = line.index(keyword)
            nisa_value = line[idx:].strip()
            line = line[:idx].strip()  # remove NISA part from the main line
            break  # only extract first matching keyword

    # Step 2: Match key-value pairs
    pattern = r'(' + '|'.join(Japan_ETF_known_keys) + r'):(.*?)(?=' + '|'.join(Japan_ETF_known_keys) + r':|$)'
    matches = re.findall(pattern, line)

    # Step 3: Build dictionary and clean values
    data_dict = {k: v.strip().replace("，", ".") for k, v in matches}

    # Step 4: Ensure we always return values in the expected key order
    result = []
    for key in Japan_ETF_known_keys:
        val = data_dict.get(key, "")
        # Inject NISA keyword into 特定区分 if it's missing
        if key == "特定区分" and val == "" and nisa_value:
            val = nisa_value
        result.append(val)

    #print("After:", result)
    return result