#!/usr/bin/env bash

# bash create new region defined parameter files (ini)

#authors: Huang Lingcao
#email:huanglingcao@gmail.com
#add time: 8 February, 2021

# Exit immediately if a command exits with a non-zero status. E: error trace
set -eE -o functrace

py=~/codes/PycharmProjects/Landuse_DL/utility/create_region_ini.py


function new_ini(){
    dir=$1
    template_ini=$2
    remark=$3
    ${py} ${dir} ${template_ini} -r ${remark}
}

region=Willow_River
dir=~/Data/Arctic/canada_arctic/rsImages/daily_mosaic/WR_daily_mosaic_8bit_nirGB
remark=nirGB_2020
ref_ini=~/codes/PycharmProjects/Landuse_DL/ini_files/area_Willow_River.ini
new_ini ${dir} ${ref_ini} ${remark}

dir=~/Data/Arctic/canada_arctic/rsImages/daily_mosaic/WR_daily_mosaic_8bit_rgb
remark=rgb_2020
new_ini ${dir} ${ref_ini} ${remark}


#region=Banks_east
#ext_shp=
#meta  ${ext_shp} ${region}
#
#
#region=Ellesmere_Island
#ext_shp=
#meta  ${ext_shp} ${region}



