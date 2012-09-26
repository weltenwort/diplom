#!/bin/zsh

CMD="python benchmark.py results collect"
TARGET_DIR="../../thesis/results"

eval "$CMD r_g_luma_mean* > ${TARGET_DIR}/g_luma_mean_1.csv"
eval "$CMD r_g_luma_sobel*_mean_* > ${TARGET_DIR}/g_luma_sobel_mean_1.csv"
eval "$CMD r_g_luma_canny*_mean_* > ${TARGET_DIR}/g_luma_canny_mean_1.csv"
eval "$CMD r_l_luma_canny*_pmean_* > ${TARGET_DIR}/l_luma_canny_pmean_1.csv"
