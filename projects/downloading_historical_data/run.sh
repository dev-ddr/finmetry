#!/bin/bash

# python download_for_multiple_stocks.py \
#     --symbols_list_filepath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/projects/downloading_historical_data/symbols_list1.txt" \
#     --local_data_foldpath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data" \
#     --creds_filepath "/home/darshan-rathod/Desktop/synodrive/discipline_is_the_key/configs/5paisa_creds_account2.yaml" \
#     --start_date "2018-01-01" \
#     --end_date "2026-01-14" \
#     --interval "one_day" \


python download_for_multiple_stocks.py \
    --symbols_list_filepath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/list_of_symbols/symlist_combined_data1.txt" \
    --local_data_foldpath "/home/darshan-rathod/Desktop/synodrive/ddr_modules/finmetry/data/historical_data" \
    --creds_filepath "/home/darshan-rathod/Desktop/synodrive/discipline_is_the_key/configs/5paisa_creds_account2.yaml" \
    --start_date "2018-01-01" \
    --end_date "2026-01-14" \
    --interval "one_day" \