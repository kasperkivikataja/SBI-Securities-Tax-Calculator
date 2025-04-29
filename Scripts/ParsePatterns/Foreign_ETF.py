## Foreign ETF markers to know where data starts/ends
Foreign_ETF_start_marker = "お問合せ先："
Foreign_ETF_end_marker = "＊＊   以 　 上   ＊＊"
Foreign_ETF_chunk_size = 46 # We parse foreign data in such a way that we should have 46 items per ?

# Pattern 4a) Foreign ETF <Header, Value> row index mapping
# The reason is that data is extracted in an inconsistent order, hence the need to map it. The mapping also helps in case the order changes in the future.

foreignETF_header_value_mapping = {
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