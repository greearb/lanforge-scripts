#!/bin/bash
TEST_DIR=$1
CSV=$2
PNG_DIR=$3
BANDWIDTH=$4
CHANNEL=$5
ANTENNA=$6

python3 parser2.py --test_dir "$TEST_DIR" --csv "$CSV" --bandwidth "$BANDWIDTH" \
	--channel "$CHANNEL" --antenna "$ANTENNA"
python3 processing.py --csv "$CSV" --png_dir "$PNG_DIR" --bandwidth "$BANDWIDTH" \
	--channel "$CHANNEL" --antenna "$ANTENNA"
