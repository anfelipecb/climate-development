# Andrés Felipe Camacho Baquero

## Description

This projects aims to show how the change in temperature anomalies can impact both the environment and socioeconomic development. The project will focus on showing:
1. Change in temperature anomalies over time
2. Spatial distribution of temperature anomalies
3. Impact between temperaure anomalies and socioeconomic development
4. Mitigation characteristics of most impacted economies
5. How this impact can be disprortional to poorer countries 


## Data Sources


### Data Source 1: ERA5 Monthly Aggregates

URL: [ERA5](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_MONTHLY)

Size: All the world at 27km resolution, 9 columns

{Short Description, including any exploration you've done already}

### Data Source 2: Meta Relative Wealth Index (RWI)

URL: [RWI](https://dataforgood.facebook.com/dfg/docs/tutorial-calculating-population-weighted-relative-wealth-index)
Data: [Data]https://data.humdata.org/dataset/relative-wealth-index
Size: All the world (pixels 2.4 km resolution), 4 Columns

The Relative Wealth Index predicts the relative standard of living within low and middle income countries at a 2.4km resolution using Meta's data ans satellite imagery. I have worked with this data before.

### Data Source 3: Hansen Global Dataset: Tree Cover Change

URL: [Global Forest Change](https://glad.earthengine.app/view/global-forest-change#bl=off;old=off;dl=1;lon=20;lat=10;zoom=3;)

Size: All the world (pixels at 30m resolution), 1 columns

Trees are defined as vegetation taller than 5m in height and are expressed as a percentage per output grid cell as ‘2000 Percent Tree Cover’. ‘Forest Cover Loss’ is defined as a stand-replacement disturbance, or a change from a forest to non-forest state, during the period 2000–2024. I have already worked with this dataset.

### Data Source 4: Demographic and Health Surveys (DHS) 

URL: [Spatial Data] https://spatialdata.dhsprogram.com/home/
Size: The DHS Program has released GPS (cluster‐level) datasets for 200+ surveys across ~63 countries.

Contains a detailed question about distance to water, source of drinking, food security, economic status.

## Questions


1. Should I have any categorical data to satisfy the final requirements?
2. Should I reduce the area of anaysis or can I keep working with the complete dataset in Google Earth Engine?
3. 