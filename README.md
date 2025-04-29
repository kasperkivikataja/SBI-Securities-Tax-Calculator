**What**:
The SBI Securities Tax Calculator is a free automation tool designed to calculate taxes for users of “Ippan Koza” accounts. Those using “Ippan Koza” accounts are responsible for reporting their earnings to the tax authorities each year.

**Why**:
Although SBI Securities provides CSV data of trades, these CSV files often differ and may not include all necessary information. For example, CSVs for foreign ETFs might exclude fees that can be deducted from Profit & Loss calculations. This software helps by:
- Calculating Profit & Loss data for “Ippan Koza” accounts
- Verifying your own tax calculations

**How**:
Fortunately, SBI Securities provides complete trade data in PDF format. This tool works by:

- Extracting all trade data from PDFs into CSV files (via Python script)
- Calculating Profit & Loss based on the CSV file using a Google Sheet (JavaScript / Google Apps Script)
