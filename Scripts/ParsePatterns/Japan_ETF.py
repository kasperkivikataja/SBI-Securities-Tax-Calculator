import unicodedata
import re
from Scripts import StringHelper

## Japan ETF markets to know where data starts/ends
Japan_ETF_startIndex = 11
Japan_ETF_end_marker1 = "◎投資信託は元金や利回りが保証されているものではありません。"
Japan_ETF_end_marker2 = "以下余白"
Japan_ETF_expected_value_count = 15 # 14 + 1 values + PDF name in the end

Japan_ETF_headers = [
    ""
]

Japan_ETF_unwanted_headers = [
    ""
]

Japan_ETF_known_keys = ['市場', '取引', '受渡条件', '特定区分', '譲渡益税区分']
Japan_ETF_extra_keywords = ['NISA成長投資枠']  # Standalone labels that can appear after values
Japan_ETF_required_keys = {'市場', '取引', '受渡条件'}

def parse_values_from_japan_etf(lines, pdf_name):
    final_values = []

    # 1. Add initial dates. These exist only at the start of the page.
    final_values.append(clean_line(StringHelper.clean_date_string(lines[6])))  # 約定日
    final_values.append(clean_line(StringHelper.clean_date_string(lines[7])))  # ご精算日

    # 2. Combine index 8 and 9 as they are part of 銘柄名
    final_values.append(clean_line(lines[8] + lines[9]))

    # 3. Separate three integers
    values = lines[10].split()
    if len(values) == 3:
        for value in values:
            value = clean_line(value)
            final_values.append(value)

    # 4. Clean 銘柄コード parenthesis and empty spaces
    ticker = clean_line(lines[11])
    ticker = clean_parenthesis(ticker)
    final_values.append(ticker)

    # 5. Add buy/sell
    final_values.append(clean_line(lines[12]))
    final_values.append(clean_line(lines[13]))

    # 6. Clean ['市場', '取引', '受渡条件', '特定区分', '譲渡益税区分']
    market_data = clean_line(lines[14])
    market_data = clean_market_data(market_data)
    final_values.extend(market_data)

    # 7. Add PDF
    final_values.insert(0, pdf_name)

    print(final_values)

    exit()
    return final_values


def clean_line(line):
    newLine = line.strip()
    newLine = unicodedata.normalize('NFKC', newLine)
    newLine = newLine.replace(",", ".")
    newLine = newLine.replace(" ", "")
    return newLine

def clean_parenthesis(line):
    newLine = line.replace("(", "")
    newLine = newLine.replace(")", "")
    return newLine

def clean_market_data(line):
    print("Market Data Before: ", line)

    # Match key:value pairs (up to the next known key or end of line)
    pattern = r'(?:' + '|'.join(Japan_ETF_known_keys) + r'):[^:]+?(?=(?:' + '|'.join(Japan_ETF_known_keys) + r')\:|$)'
    values = re.findall(pattern, line)
    values = [v.strip().replace("，", ".") for v in values]

    # Post-process: split off any extra keywords attached after a value
    return_values = []
    for v in values:
        for keyword in Japan_ETF_extra_keywords:
            if keyword in v and not v.startswith(keyword):
                # Split and append both parts
                before, after = v.split(keyword, 1)
                return_values.append(before.strip())
                return_values.append(keyword)
                break
        else:
            return_values.append(v)
    print("After: ", return_values)
    return return_values