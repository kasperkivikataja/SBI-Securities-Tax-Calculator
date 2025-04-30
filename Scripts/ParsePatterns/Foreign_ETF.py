## Foreign ETF markers to know where data starts/ends
import unicodedata

Foreign_ETF_start_marker = "取引通貨"
Foreign_ETF_end_marker = "**   以   上   **"
Foreign_ETF_expected_value_count = 23

# Pattern 4a) Foreign ETF <Header, Value> row index mapping
# The reason is that data is extracted in an inconsistent order, hence the need to map it. The mapping also helps in case the order changes in the future.

Foreign_ETF_headers = [
    "国内約定年月日", "国内受渡年月日", "現地約定年月日", "現地受渡年月日", "銘柄コード", "銘柄名", "市場", "口座区分", "自己・委託", "為替レート",
    "売買", "決済方法", "取引通貨", "約定数量", "約定価格", "約定金額", "現地手数料等", "受渡金額", "消費税", "国内手数料", "円貨 (現地精算金額)",
    "外貨 (現地精算金額)", "取引の種類"
]

Foreign_ETF_unwanted_headers = [
    "備考", "現地精算金額", "国内約定年月日国内受渡年月日", "現地約定年月日現地受渡年月日", "銘 柄 名", "円貨", "外貨"
]

# Step 4: Pattern 2) Parse Japan ETF files
# Function to parse Foreign ETF files
def parse_values_from_foreign_etf(lines):
    final_values = clean(lines)
    return final_values


def clean(lines):
    cleaned_values = []
    startmarker_found = False
    endmarker_found = False
    tradeCount = 0

    for line in lines:
        nextLine = line.strip()
        nextLine = unicodedata.normalize('NFKC', nextLine)
        nextLine = nextLine.replace(",", ".")

        if not startmarker_found:
            if Foreign_ETF_start_marker in nextLine:
                startmarker_found = True
                continue
            else:
                continue

        if not endmarker_found:
            nextLine = nextLine.strip()
            if Foreign_ETF_end_marker in nextLine:
                endmarker_found = True
                if (len(cleaned_values) * tradeCount != Foreign_ETF_expected_value_count):
                    tradeCount += 1
                    cleaned_values = add_empty_fields(tradeCount, cleaned_values)
                break
            else:
                if nextLine in Foreign_ETF_headers:
                    continue

                elif nextLine in Foreign_ETF_unwanted_headers:
                    continue

        cleaned_values.append(nextLine)
    return cleaned_values


def add_empty_fields(tradeCount, cleaned_values):
    insert_index = 13 * tradeCount
    cleaned_values.insert(insert_index, "Empty (区分)")
    return cleaned_values
