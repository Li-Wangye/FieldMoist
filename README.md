# FieldMoist

Startup: [English](STARTUP.md) | [Chinese](STARTUP.zh-CN.md)  
First Installation Guide: [English](First Installation Guide.md) | [Chinese](首次安装指导.md)  
Printable HTML: [English](First Installation Guide.html) | [Chinese](首次安装指导.html)  
Chinese README: [README.zh-CN.md](README.zh-CN.md)

These files are technical reference documentation. FieldMoist is a display-only release; see [LICENSE](LICENSE) for the rights notice.

## Project Purpose

FieldMoist is a web system for generating daily farmland soil-moisture products. This release provides the **jiefangzha** display area (polygon 83), with 24 daily products from 2018-05-01 through 2018-05-24. It also includes an offline `test` workflow for project 82 that can reproduce the **jiefangzha** display area.

The website supports daily map browsing, point-based soil-moisture and NASA POWER time series, GeoTIFF downloads, and optional AMap satellite or standard basemaps. Existing local PNG products and the offline `test` do not depend on GEE or require the AMap basemap to be available.

## Environment and Components

- Windows 10/11 x64 with Python 3.12 x64
- Miniconda or Anaconda, using the supplied `environment.yml`
- Node.js 22.12 or newer and npm
- Public application code plus an authorized, version-matched private compiled core
- Companion data packages extracted under `backend/media`
- Optional AMap JavaScript API key and security code for the basemap
- Optional Google Earth Engine project and authentication for Online processing

The backend uses Django and Django REST Framework. The frontend is built with Vue 3 and Vite, integrates Tailwind CSS, and uses ECharts for visualization. GDAL, Rasterio, GeoPandas and related geospatial libraries process raster and vector data; NumPy, pandas, SciPy and scikit-learn provide scientific analysis and model computation. SQLite is used for lightweight display and can be switched to MySQL when necessary.

## Repository Layout

```text
FieldMoist/
├── backend/                          Django API and processing pipeline
├── frontend/                         Vue/Vite web application
├── tools/                            validation, core installation and smoke checks
├── environment.yml                  recommended Conda environment
├── STARTUP.md                        short startup guide (English)
├── STARTUP.zh-CN.md                  short startup guide (Chinese)
├── 首次安装指导.md                    First Installation Guide (Chinese)
├── First Installation Guide.md       First Installation Guide (English)
├── 首次安装指导.html                  printable First Installation Guide (Chinese)
├── First Installation Guide.html     printable First Installation Guide (English)
├── README.md                         English project overview
└── README.zh-CN.md                   Chinese project overview
```

## Quick Start

For a first installation, read the [First Installation Guide](First Installation Guide.md). It explains how to obtain the public/private files and data, install the private algorithm, configure `.env`, validate data, initialize the database, start the backend and frontend, and run the offline `test`.

From the `public` directory, run the core commands:

```bat
conda env create -f environment.yml
conda activate FieldMoist
python tools/install_core.py --from-dir ..\private
python tools/smoke_native_core.py
copy .env.example .env
copy frontend\.env.example frontend\.env
python backend/manage.py validate_fieldmoist_data --dataset all
python backend/manage.py migrate
python backend/manage.py seed_fieldmoist
python backend/manage.py check
npm ci --prefix frontend
npm run build --prefix frontend
```

Start the backend and frontend in two separate Anaconda Prompt windows:

```bat
python backend/manage.py runserver 127.0.0.1:8000 --noreload
```

```bat
npm run dev --prefix frontend -- --host 127.0.0.1 --port 5173 --strictPort
```

Open <http://127.0.0.1:5173/>. The local display and offline `test` do not require GEE authentication.

## Operating Instructions

### jiefangzha Display Area

After starting both services, open the `Explore` page. A correct display has the following characteristics:

1. The header shows `FieldMoist`, and the status on the right is `API connected`.
2. The study-area name is `jiefangzha`, with a red-white-blue soil-moisture product on the map.
3. The initial date is `2018-05-01`; use the left and right arrows to change dates.
4. The page shows `Dataset ID 83`, `24 daily products`, and a color scale of `0.00`–`0.40 m³/m³`.
5. `Download GeoTIFF` downloads the raster for the selected date.
6. `Satellite` and `Standard` change only the AMap basemap, not the soil-moisture product.

If the 24 dated products are available but the basemap is blank, check the network, AMap key and security code. The local colored product can still be displayed independently.

![Daily soil-moisture products for the jiefangzha display area](fig/FieldMoist01.png)

![Product browsing and analysis for the jiefangzha display area](fig/FieldMoist02.png)

### Reproduce the jiefangzha Display Area

Use the project 82 offline `test` preset to reproduce the display area:

1. Confirm that both services are running and that the display area above opens correctly.
2. Select `Generate` in the top navigation, then choose `Offline` under `Processing mode`.
3. Enter lowercase `test` in `Area name`, click outside the input, and wait for the preset to load.
4. Confirm that the boundary, local paths, and dates from `2018-05-01` through `2018-05-24` were filled automatically.
5. When `Offline test dataset is ready. Click Start generation.` appears, click `Start generation`.
6. Keep both command windows open until the status is `Completed` and progress reaches 100%.
7. Click `View generated result` to inspect the reproduced result.

Do not manually upload SMAP, Sentinel, boundary or Excel files. Do not change the preset dates or change project 82 to 83. The backend prints only stage summaries, so a short period without new output is normal. Do not let the computer sleep, close the backend, or submit duplicate tasks while processing.

![Reproducing the jiefangzha display area with the offline test](fig/FieldMoist03.png)

For a fresh standard installation, results are saved in:

```text
C:\FieldMoist\public\backend\media\images\82\2018-05-01_2018-05-24\soil_moisture_result\
C:\FieldMoist\public\backend\media\images\82\2018-05-01_2018-05-24\soil_moisture_png\
```

The first directory should contain 24 dated `.tif` files and the second should contain 24 `.png` files. Intermediate output remains in the adjacent `process` directory and does not need to be moved. `ml_patch_report.xlsx` is not generated by default; the station measurement workbook is still required as input.

## Online Processing

Online mode requires an Earth Engine-enabled Google Cloud project. Set `EARTH_ENGINE_PROJECT` in the backend `.env`, then run `python tools/authorize_earth_engine.py`. GEE authentication and satellite downloads require a network that can reach Google Earth Engine; this is separate from AMap availability. NASA POWER uses local caches first and only needs network access for uncovered cells or dates.

## Data and Rights

Raster, boundary, model and cache files are supplied separately from the source. The required directory layout and file counts are listed in the First Installation Guide; if the companion directory is present, see [backend/media/README.md](backend/media/README.md). Do not substitute same-named files, create empty placeholders, or mix project 82 and project 83 directories.

Test data: <https://huggingface.co/datasets/LiWangye/FieldMoist>

The public application and private compiled core are separate deliveries. Before using or redistributing imagery, models or derived products, confirm that you have the necessary permissions. Contact the author about access to the compiled core; access may be granted depending on the circumstances. The project and compiled core reserve all rights; technical instructions do not constitute a license.

## Citation and Support

Use the metadata in [CITATION.cff](CITATION.cff) when citing the project. For questions, consult the First Installation Guide and provide the exact command, Python version, task ID and relevant error lines.
