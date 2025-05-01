import unicodedata
from datetime import datetime

Foreign_ETF_start_marker = "取引通貨"
Foreign_ETF_end_marker = "**   以   上   **"
Foreign_ETF_expected_value_count = 24 # 23 values + PDF name in the end

Foreign_ETF_headers = [
    "国内約定年月日", "国内受渡年月日", "現地約定年月日", "現地受渡年月日", "銘柄コード", "銘柄名", "取引の種類", "取引通貨", "売買", "決済方法",
    "自己・委託", "為替レート", "市場", "口座区分", "約定数量", "約定価格", "約定金額", "現地手数料等", "外貨 (現地精算金額)", "円貨 (現地精算金額)", "国内手数料",
    "消費税", "受渡金額"
]

Foreign_ETF_unwanted_headers = [
    "備考", "現地精算金額", "国内約定年月日国内受渡年月日", "現地約定年月日現地受渡年月日", "銘 柄 名", "円貨", "外貨"
]

# Step 4: Pattern 2) Parse Japan ETF files
# Function to parse Foreign ETF files
def parse_values_from_foreign_etf(lines, pdf_name):
    final_values = []
    startmarker_found = False
    endmarker_found = False
    tradeCount = 1
    trade_endmarker_count = 0

    for line in lines:
        nextLine = line.strip()
        nextLine = unicodedata.normalize('NFKC', nextLine)
        nextLine = nextLine.replace(",", ".")

        if not startmarker_found:
            if Foreign_ETF_start_marker in nextLine:
                startmarker_found = True
                final_values.append(pdf_name)
                continue
            else:
                continue

        if not endmarker_found:
            nextLine = nextLine.strip()

            if is_date(nextLine):
                missing_Kubun_And_PDF_name = len(final_values) is tradeCount * 23 # We know we have reached then end when the count divided by 23 or 24

                if missing_Kubun_And_PDF_name:
                    final_values = add_empty_fields(tradeCount, final_values)
                    final_values.insert(len(final_values), pdf_name)
                    tradeCount += 1

            elif Foreign_ETF_end_marker in nextLine:
                missing_Kubun_And_PDF_name = len(final_values) is tradeCount * 23  # We know we have reached then end when the count divided by 23 or 24
                if missing_Kubun_And_PDF_name:
                    final_values = add_empty_fields(tradeCount, final_values)
                break
            else:
                if nextLine in Foreign_ETF_headers:
                    continue

                elif nextLine in Foreign_ETF_unwanted_headers:
                    continue

        final_values.append(nextLine)

    return final_values



def add_empty_fields(tradeCount, final_values):
    insert_index = 14 * tradeCount
    final_values.insert(insert_index, "Empty (区分)")
    return final_values

def is_date(string):
    try:
        datetime.strptime(string, "%Y/%m/%d")
        return True
    except ValueError:
        return False