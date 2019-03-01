#!/usr/bin/env bash

# add attributes to polygons

#authors: Huang Lingcao
#email:huanglingcao@gmail.com
#add time: 25 February, 2019

# Exit immediately if a command exits with a non-zero status. E: error trace
set -eE -o functrace

code_dir=~/codes/PycharmProjects/Landuse_DL
# folder contains results
res_dir=~/Data/Qinghai-Tibet/beiluhe/result/result_paper_mapping_RTS_dl_beiluhe

### polygons
# the 202 ground truth polygons
ground_truth=${res_dir}/identified_ThawSlumps_prj_post.shp
#polygon_shp=${res_dir}/identified_ThawSlumps_prj_post.shp
# the 165 true positives
polygon_shp=${res_dir}/img_aug_test_results/BLH_basin_deeplabV3+_1_exp9_iter30000_post_imgAug16_TP.shp

# polyon with post-processing (removing polygons based on their areas)
shp_imgAug16_NOpost=${res_dir}/img_aug_test_results/BLH_basin_deeplabV3+_1_exp9_iter30000_imgAug16.shp
shp_imgAug17_NOpost=${res_dir}/img_aug_test_results/BLH_basin_deeplabV3+_1_exp9_iter30000_imgAug17.shp

################################################################################
### polygon geometric information and IoU

#${code_dir}/resultScript/add_info2Pylygons.py ${shp_imgAug16_NOpost} -v ${ground_truth} -n "IoU"

${code_dir}/resultScript/add_info2Pylygons.py ${shp_imgAug17_NOpost} -v ${ground_truth} -n "IoU"

################################################################################
### raster
pisr=~/Data/Qinghai-Tibet/beiluhe/DEM/srtm_30/dem_derived/beiluhe_srtm30_utm_basinExt_PISR_total_perDay.tif
tpi=~/Data/Qinghai-Tibet/beiluhe/DEM/srtm_30/dem_derived/beiluhe_srtm30_utm_basinExt_tpi.tif

dem=~/Data/Qinghai-Tibet/beiluhe/DEM/srtm_30/beiluhe_srtm30_utm_basinExt.tif
slope=~/Data/Qinghai-Tibet/beiluhe/DEM/srtm_30/beiluhe_srtm30_utm_basinExt_slope.tif
aspect=~/Data/Qinghai-Tibet/beiluhe/DEM/srtm_30/beiluhe_srtm30_utm_basinExt_apect.tif

# inside polygons
#${code_dir}/resultScript/add_info2Pylygons.py ${polygon_shp} -r ${pisr} -n "pisr"
#
#${code_dir}/resultScript/add_info2Pylygons.py ${polygon_shp} -r ${tpi} -n "tpi"
#
#${code_dir}/resultScript/add_info2Pylygons.py ${polygon_shp} -r ${slope} -n "slo"
#
#${code_dir}/resultScript/add_info2Pylygons.py ${polygon_shp} -r ${dem} -n "dem"
#
#${code_dir}/resultScript/add_info2Pylygons.py ${polygon_shp} -r ${aspect} -n "asp"



# in the buffer area
#./add_info2Pylygons.py ${polygon_shp} -r ${pisr} -n "pisr" -b 30


################################################################################
