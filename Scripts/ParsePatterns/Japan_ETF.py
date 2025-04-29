import unicodedata
import re
from Scripts import StringHelper

## Japan ETF markets to know where data starts/ends
Japan_ETF_startIndex = 8
Japan_ETF_end_marker1 = "◎投資信託は元金や利回りが保証されているものではありません。"
Japan_ETF_end_marker2 = "以下余白"

# Pattern 4b) Japan ETF <Header, Value> row index mapping
# The reason is that data is extracted in an inconsistent order, hence the need to map it. The mapping also helps in case the order changes in the future.
# <TBD>

Japan_ETF_header_value_mapping = {
    6: 0, # (Header) 約定日
    7: 0, # (Header) ご精算日
        0: 8, # (Value) 銘柄名（銘柄コード） (Same as below)
        0: 9, # (Value) (Same as above)
        0: 10 # (Value)
}

def parse_text_from_japan_etf(lines):
    filtered_lines = []

    index = Japan_ETF_startIndex

    # Add initial dates. These exist only at the start of the page.
    date1 = StringHelper.clean_date_string(lines[6]) # 約定日
    date2 = StringHelper.clean_date_string(lines[7]) # ご精算日

    for line in lines[Japan_ETF_startIndex:]: # We start at index 6
        line = unicodedata.normalize('NFKC', line)
        line = line.strip()

        # A page  can end in two patterns
        if (line == Japan_ETF_end_marker1 or line == Japan_ETF_end_marker2):
            return filtered_lines

        # Check end marker first
        tradeEndMarker = all(key in line for key in ["市場", "取引", "受渡条件"]) # We find last, trade ends here
        if (tradeEndMarker):
            # Define known keys
            known_keys = ['市場', '取引', '受渡条件', '特定区分', '譲渡益税区分']
            extra_keywords = ['NISA成長投資枠']  # Standalone labels that can appear after values
            required_keys = {'市場', '取引', '受渡条件'}

            # Match key:value pairs (up to the next known key or end of line)
            pattern = r'(?:' + '|'.join(known_keys) + r'):[^:]+?(?=(?:' + '|'.join(known_keys) + r')\:|$)'
            values = re.findall(pattern, line)
            values = [v.strip().replace("，", ".") for v in values]

            # Post-process: split off any extra keywords attached after a value
            final_values = []
            for v in values:
                for keyword in extra_keywords:
                    if keyword in v and not v.startswith(keyword):
                        # Split and append both parts
                        before, after = v.split(keyword, 1)
                        final_values.append(before.strip())
                        final_values.append(keyword)
                        break
                else:
                    final_values.append(v)

            # Validate required keys
            found_keys = {v.split(":")[0] for v in final_values if ":" in v}
            if required_keys.issubset(found_keys):
                filtered_lines.extend(final_values)
                index = Japan_ETF_startIndex
                continue
            else:
                print("Error: Missing required keys. Found:", final_values)
                exit(1)

        elif (index == Japan_ETF_startIndex):
            filtered_lines.append(date1)
            filtered_lines.append(date2)

        elif (index == 10): # 数量, 単価, 約定金額
            values = lines[10].split()
            if len(values) == 3:
                values = [v.replace("，", ".") for v in values]
                filtered_lines.extend(values[:3])
        else:
            filtered_lines.append(line)

        index += 1


    print("Error: Ran into exit. This should not happen.")
    exit()
    return null