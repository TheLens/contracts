csvcut -C 1 raw_contract_log.csv  | grep -v "PO Number" | grep -v '"' > raw_contract_log_processed.csv
