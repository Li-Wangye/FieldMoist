# FieldMoist

Startup: [English](STARTUP.md) | [Chinese](STARTUP.zh-CN.md).
Beginner manual: [English](BEGINNER_GUIDE.md) | [Chinese](新手安装与使用手册.md).
Printable HTML: [English](BEGINNER_GUIDE.html) | [Chinese](新手安装与使用手册.html).
These are technical reference documents; see the display-only [rights notice](LICENSE).


**A Web-Based System for Generating and Visualizing Daily Farmland Soil Moisture Products**

FieldMoist is a research-oriented web system for managing a farmland boundary, generating daily soil-moisture products from multi-source remote-sensing data, and interactively examining the resulting GeoTIFF and PNG time series. This release contains one registered study area, **jiefangzha** (polygon ID 83), with 24 daily products from **2018-05-01 through 2018-05-24** (result set ID 83).

## Features

- Daily 100 m soil-moisture map exploration with an authoritative simplified field boundary
- Regional minimum, mean, and maximum statistics for each daily product
- Point-based soil-moisture, rainfall, and NASA POWER time-series analysis
- Region-wide NASA POWER grid-cell pre-download and local cache for point analysis
- GeoTIFF download for reproducible downstream analysis
- Red → white → blue color scale fixed to 0.00–0.40 m³/m³
- Satellite basemap by default, with an in-map switch to the standard AMap basemap
- SQLite-first setup for reproducible local use, with optional MySQL support
- Environment-based secrets and API configuration

## Technology

- Frontend: Vue 3, Vite, ECharts, AMap JavaScript API
- Backend: Django 5, Django REST Framework
- Geospatial processing: GDAL, Rasterio, GeoPandas, Shapely
- Scientific processing: NumPy, pandas, SciPy, scikit-learn
- External observations: Google Earth Engine and NASA POWER

## Quick Start

This application supports **Windows x64 with Python 3.12 only**. This public
repository contains the application source; compiled algorithms are stored in
a separate private repository. Authorized access to the matching private core
is required to run the backend. Companion data is downloaded separately.
Neither repository contains core source. See [core installation](docs/WINDOWS_CORE.md).

See [STARTUP.md](STARTUP.md) for the complete English guide or [STARTUP.zh-CN.md](STARTUP.zh-CN.md) for the Chinese guide.

```powershell
conda env create -f environment.yml
conda activate FieldMoist
python tools/install_core.py --from-dir ../private
python tools/smoke_native_core.py
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env
python backend/manage.py migrate
python backend/manage.py validate_fieldmoist_data --dataset all
python backend/manage.py seed_fieldmoist
npm ci --prefix frontend
```

Start the backend and frontend in separate PowerShell windows:

```powershell
conda activate FieldMoist
python backend/manage.py runserver 0.0.0.0:8000
```

```powershell
npm run dev --prefix frontend
```

Open `http://localhost:5173` on the host machine.

For first-time GEE authorization, configure `EARTH_ENGINE_PROJECT` in `.env`,
then run `python tools/authorize_earth_engine.py`. Pay attention to your network
environment: GEE may be unreachable from networks in mainland China. Offline
`test` processing does not need GEE. Cached NASA POWER data is reused locally; Amap is optional for displaying the basemap.

## Data

The raster dataset is intentionally excluded from Git. Its required directory layout, validation rules, and boundary policy are documented in [backend/media/README.md](backend/media/README.md). Confirm that you have permission to redistribute the imagery, model files, and derived products before publishing them separately.

## Repository Layout

```text
FieldMoist/
├── backend/              Django API and processing pipeline
├── frontend/             Vue user interface
├── environment.yml       Recommended Conda environment
├── requirements.txt      Python package reference
├── STARTUP.md            English setup guide
└── STARTUP.zh-CN.md      Chinese setup guide
```

## Citation

Use the metadata in [CITATION.cff](CITATION.cff). Add the paper DOI and repository URL after they are assigned.

## Contributing and Security

See the project notice in [CONTRIBUTING.md](CONTRIBUTING.md). Report security issues according to [SECURITY.md](SECURITY.md), not through a public issue.

## Rights Notice

FieldMoist is displayed for reference only. [LICENSE](LICENSE) reserves all
rights and grants no permission to use, execute, copy, modify or distribute
the project. The proprietary core has the same no-grant policy in its
`CORE_LICENSE.txt` / private `LICENSE.txt`. Third-party terms remain separate.
Repository access and technical startup instructions are not a license.
