#!/bin/zsh

CMD="python benchmark.py results collect"
MEANSCMD="python benchmark.py results collectmeans"
TARGET_DIR="../../thesis/results"

eval "$CMD r_g_luma_mean* > ${TARGET_DIR}/g_luma_mean_1.csv"
eval "$CMD r_g_luma_segment_mean_* > ${TARGET_DIR}/g_luma_segment_mean_1.csv"
eval "$CMD r_g_luma_sobel*_mean_* > ${TARGET_DIR}/g_luma_sobel_mean_1.csv"
eval "$CMD r_g_luma_canny*_mean_* > ${TARGET_DIR}/g_luma_canny_mean_1.csv"
eval "$CMD r_l_luma_pmean_* > ${TARGET_DIR}/l_luma_pmean_1.csv"
eval "$CMD r_l_luma_pmean2_* > ${TARGET_DIR}/l_luma_pmean2_1.csv"
eval "$CMD r_l_luma_segment_pmean_* > ${TARGET_DIR}/l_luma_segment_pmean_1.csv"
eval "$CMD r_l_luma_segment_pmean2_* > ${TARGET_DIR}/l_luma_segment_pmean2_1.csv"
eval "$CMD r_l_luma_sobel_pmean_* > ${TARGET_DIR}/l_luma_sobel_pmean_1.csv"
eval "$CMD r_l_luma_sobel_pmean2_* > ${TARGET_DIR}/l_luma_sobel_pmean2_1.csv"
eval "$CMD r_l_luma_canny_1_5_pmean_g8_3_*_s4_a12* > ${TARGET_DIR}/l_luma_canny_pmean_1.csv"
eval "$CMD r_l_luma_canny_1_5_pmean2_g8_3_*_s4_a12* > ${TARGET_DIR}/l_luma_canny_pmean2_1.csv"
eval "$CMD\
    r_g_luma_mean_g12_cos_s4_a12*.json\
    r_g_luma_canny_1_5_mean_g8_cos_s4_a12*.json\
    r_g_luma_sobel_mean_g12_cos_s4_a12*.json\
    r_l_luma_canny_1_5_pmean_g8_3_hi_1000_itf_s4_a12*.json\
    r_l_luma_canny_1_5_pmean2_g8_3_cos_1000_itf_s4_a12*.json\
    r_l_luma_sobel_pmean_g8_3_hibin_1000_itf_s4_a12*.json\
    > ${TARGET_DIR}/best_performers.csv"
eval "$MEANSCMD\
    r_g_luma_mean_g12_cos_s4_a12*.json\
    r_g_luma_canny_1_5_mean_g8_cos_s4_a12*.json\
    r_g_luma_sobel_mean_g12_cos_s4_a12*.json\
    r_l_luma_canny_1_5_pmean_g8_3_hi_1000_itf_s4_a12*.json\
    r_l_luma_canny_1_5_pmean2_g8_3_cos_1000_itf_s4_a12*.json\
    r_l_luma_sobel_pmean_g8_3_hibin_1000_itf_s4_a12*.json\
    > ${TARGET_DIR}/best_performer_means.csv"
eval "$CMD\
    r_l_luma_canny_1_5_pmean_g8_3_hi_1000_itf_s4_a*.json\
    > ${TARGET_DIR}/parameter_angles.csv"
eval "$CMD\
    r_l_luma_canny_1_5_pmean_g*_*_hi_*_s4_a12*.json\
    > ${TARGET_DIR}/parameter_grid.csv"
eval "$CMD\
    r_l_luma_canny_*_pmean_g8_3_hi_*_s4_a12*.json\
    > ${TARGET_DIR}/parameter_canny.csv"
