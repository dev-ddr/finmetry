#!/bin/bash

python download_for_multiple_stocks.py \
    --symbols_list_filepath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/list_of_symbols/futures_traded_symbols.txt" \
    --local_data_foldpath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data" \
    --creds_filepath "/home/darshan-rathod/Desktop/synodrive/discipline_is_the_key/configs/5paisa_creds_account2.yaml" \
    --start_date "2017-01-01" \
    --end_date "2026-01-19" \
    --interval "one_day" \
    --overwrite "false" \


# python download_for_multiple_stocks.py \
#     --symbols_list_filepath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/list_of_symbols/symlist_combined_data1.txt" \
#     --local_data_foldpath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data" \
#     --creds_filepath "/home/darshan-rathod/Desktop/synodrive/discipline_is_the_key/configs/5paisa_creds_account2.yaml" \
#     --start_date "2017-01-01" \
#     --end_date "2026-01-19" \
#     --interval "one_day" \
#     --overwrite "false" \
#     --overwrite "true" \