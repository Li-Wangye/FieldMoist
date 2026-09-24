# FieldMoist Startup Guide

Language: English | [Other language](STARTUP.zh-CN.md).

This is technical reference documentation only. The project is display-only;
the rights notice grants no permission to run, modify or redistribute it.


## Prerequisites

- Windows 10/11 x64 with PowerShell; bundled algorithms require CPython 3.12 x64
- Miniconda or Anaconda
- Node.js 22.12 or newer and npm
- An AMap JavaScript API key and security code for the basemap
- The FieldMoist raster dataset in the directory described below

The default setup uses SQLite. MySQL is optional and is not required for the bundled study area.

## 1. Create the Python environment

From the repository root:

```powershell
conda env create -f environment.yml
conda activate FieldMoist
```

The Conda file is recommended because GDAL and Rasterio must use compatible native libraries.

The new environment is named `FieldMoist`; the existing maintainer environment
is `SoilMoisturePlatform`. Obtain authorized access to the matching private
core repository and extract it alongside this public checkout. Then run:

```powershell
python tools/install_core.py --from-dir ../private
python tools/smoke_native_core.py
```

Replace `../private` with the actual private checkout path. Cython and a compiler
are not required on the user's machine. Download the companion data separately.
See [Windows core installation](docs/WINDOWS_CORE.md). Public code alone cannot
run algorithm-dependent backend commands until the private core is installed.

## 2. Configure the backend

```powershell
Copy-Item .env.example .env
```

For local development, the defaults are sufficient. Before deployment, replace `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, and set the public host/origin values.

To create new products from the `Generate` workspace, set `EARTH_ENGINE_PROJECT` to your Google Cloud project. For interactive local development, run `earthengine authenticate`; the backend will use that local credential. For unattended jobs, set both `EARTH_ENGINE_SERVICE_ACCOUNT` and `EARTH_ENGINE_CREDENTIALS_FILE` (or the standard `GOOGLE_APPLICATION_CREDENTIALS`) in `.env`. Keep the JSON key outside Git. The required local model and ancillary raster layout is documented in `backend/media/README.md`.

The point-analysis weather panel uses NASA POWER. NASA POWER is a public service and does not require a NASA account or API key. `NASA_POWER_API_URL`, `NASA_POWER_TIMEOUT_SECONDS`, and `NASA_POWER_USER_AGENT` are configurable for institutional proxies or operational deployments. The optional `NASA_EARTHDATA_USERNAME` and `NASA_EARTHDATA_PASSWORD` entries in `.env.example` are reserved for future Earthdata integrations and are not sent to NASA POWER.

In `Generate`, choose **SHP file** to define a study area from an existing boundary. Upload one ZIP containing the `.shp`, `.shx`, `.dbf`, and `.prj` components (recommended), or select the matching components together. The `.prj` file is required so the boundary can be transformed to WGS84; the uploaded components are preserved under the new polygon's media directory.

To use MySQL, uncomment and edit the MySQL variables in `.env`, create an empty database named `fieldmoist`, and ensure the MySQL service is running. Do not commit `.env`.

## 3. Google Earth Engine First Authorization

Only Online mode needs GEE authorization. Configure `EARTH_ENGINE_PROJECT` in
`.env`, then run the equivalent of the original `authorize.py`:

```powershell
python tools/authorize_earth_engine.py
```

Complete the browser authorization with an account that has access to the
configured, Earth Engine-enabled Google Cloud project. Please check your network
environment. GEE may be unreachable from networks in mainland China. Offline
`test` processing does not require GEE authentication or GEE network access.

## 4. Configure the Frontend Map

```powershell
Copy-Item frontend/.env.example frontend/.env
```

Edit `frontend/.env` and set `VITE_AMAP_KEY` and `VITE_AMAP_SECURITY_CODE`. These browser credentials must be restricted to the domains used for the application.

## 5. Place and register the dataset

The local release expects:

```text
backend/media/images/83/shp/shp.shp
backend/media/images/83/2018-05-01_2018-05-24/soil_moisture_result/*.tif
backend/media/images/83/2018-05-01_2018-05-24/soil_moisture_png/*.png
```

There must be 24 daily TIF files and 24 matching PNG files. Then run:

```powershell
python backend/manage.py migrate
python backend/manage.py validate_fieldmoist_data --dataset all
python backend/manage.py seed_fieldmoist
python backend/manage.py check
```

The seed command registers jiefangzha from the existing boundary. It does not
delete other research areas. The companion data must also include the test
inputs listed in [the data layout](backend/media/README.md).

## 6. Install frontend dependencies

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
```

## 7. Run FieldMoist

Backend terminal:

```powershell
conda activate FieldMoist
python backend/manage.py runserver 0.0.0.0:8000
```

Frontend terminal:

```powershell
npm run dev --prefix frontend
```

Open `http://localhost:5173` on this computer. The API health endpoint is
`http://localhost:8000/api/health/`.

Verify jiefangzha and its daily maps. Then open Generate, select **Offline**,
enter `test`, wait for the preset to load and click **Start generation**.
The preset uses local SMAP, soil-moisture rasters, Excel and the shared model.
On completion, select **View generated result**. Use **Run test again** for a
fresh rerun. Existing NASA POWER cache files are reused locally; missing cells need network access. If Amap is unavailable, Explore still shows the soil-moisture product without a basemap.

The Explore workspace opens with the AMap satellite basemap used by the original SoilMoisturePlatform. Use the **Satellite / Standard** switch in the map corner to change the basemap at any time.

AMap tiles are stored in the browser's `FieldMoist AMap tiles` cache after first use. On `localhost` or HTTPS this cache is managed by the included service worker; an HTTP LAN address may rely on the browser's normal HTTP cache because browsers restrict service workers on insecure IP origins.

For offline basemap use, open the target area while online, visit both **Satellite** and **Standard** modes, and zoom/pan through the area and levels you will need. Only tiles already viewed can be displayed offline; the backend API and uncached daily products still require a network connection.

## Troubleshooting

- `npm.ps1 cannot be loaded`: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, reopen PowerShell, or invoke `npm.cmd`.
- A blank basemap: verify both AMap variables and their domain restrictions, then restart Vite.
- Missing daily products: run `python backend/manage.py validate_fieldmoist_data --dataset all` and correct the reported paths.
- Native module load error: use Windows x64 and Python 3.12 and install the matching private core with `tools/install_core.py`.
- GDAL import errors: recreate the Conda environment instead of mixing pip GDAL with a different native GDAL installation.
- NASA POWER timeout: cached cells are used first; only uncached point/time ranges need network access. Daily raster browsing remains local.

## Fresh Test Runs

Local PNG display is independent of Amap tiles and ImageLayer rendering. Each offline `test` start rebuilds generated preprocessing files, cycle caches and TIF/PNG products, preserving original inputs, the supplied shared model and NASA caches. Restart both services after updating; do not reset the database.

The selected-point ring is drawn above the product PNG, including when the basemap SDK is unavailable. Processing prints short stage messages instead of per-file progress or algorithm details. `ml_patch_report.xlsx` is disabled by default; measurement Excel inputs and moisture calculations are still used.
