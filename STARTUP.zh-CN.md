# FieldMoist 启动说明

语言：中文 | [English](STARTUP.md)。

本文件仅为技术参考。项目仅供展示，权利声明不授予运行、修改或分发许可。


没有命令行经验的用户，请使用 [新手安装与使用手册](新手安装与使用手册.md)，
其中包含软件安装、完整数据清单、私有算法安装位置和逐步操作。

## 环境要求

- Windows 10/11 x64 与 PowerShell；编译算法仅支持 Python 3.12 x64
- Miniconda 或 Anaconda
- Node.js 22.12 或更高版本，以及 npm
- 用于底图的高德地图 JavaScript API Key 和安全密钥
- 已按下述目录放置的 FieldMoist 数据

默认配置使用 SQLite，不需要启动 MySQL。只有明确需要 MySQL 时才进行切换。

## 1. 创建 Python 环境

在项目根目录运行：

```powershell
conda env create -f environment.yml
conda activate FieldMoist
```

建议使用 Conda，因为 GDAL 和 Rasterio 的本地动态库版本必须匹配。

本仓库只包含公开应用代码。获得匹配版本私有仓库的访问权限后，下载并解压，
从本项目根目录执行以下命令安装编译算法，无需安装 Cython 或编译器：

```powershell
python tools/install_core.py --from-dir ../private
python tools/smoke_native_core.py
```

将 `../private` 替换为私有仓库的实际解压路径。安装成功后再执行后续迁移和启动。
没有私有编译算法，仅下载公开代码不能运行完整后端。配套数据仍单独下载。
新环境名为 `FieldMoist`，旧的 `SoilMoisturePlatform` 环境可暂时用于维护。
详见 [Windows 发布说明](docs/WINDOWS_CORE.md)。

## 2. 配置后端

```powershell
Copy-Item .env.example .env
```

本地开发可直接使用默认配置。正式部署前必须更换 `DJANGO_SECRET_KEY`，设置 `DJANGO_DEBUG=false`，并填写实际域名和跨域来源。不要将 `.env` 提交到 Git。

如需通过 `Generate` 页面创建新产品，请将 `EARTH_ENGINE_PROJECT` 设置为自己的 Google Cloud 项目。本地交互开发可运行 `earthengine authenticate`，后端会使用本机凭据；无人值守任务请在 `.env` 中同时设置 `EARTH_ENGINE_SERVICE_ACCOUNT` 与 `EARTH_ENGINE_CREDENTIALS_FILE`（或标准变量 `GOOGLE_APPLICATION_CREDENTIALS`）。JSON 密钥文件不要提交到 Git。模型和辅助栅格目录见 `backend/media/README.md`。

点分析天气面板使用 NASA POWER。NASA POWER 是公开服务，不需要 NASA 账号或 API Key。`NASA_POWER_API_URL`、`NASA_POWER_TIMEOUT_SECONDS` 和 `NASA_POWER_USER_AGENT` 可用于配置机构代理或生产环境。`.env.example` 中可选的 `NASA_EARTHDATA_USERNAME` 与 `NASA_EARTHDATA_PASSWORD` 仅为将来的 Earthdata 接口预留，当前不会发送给 NASA POWER。

在 `Generate` 页面选择 **SHP file** 可以使用已有边界确定研究区。建议上传一个同时包含 `.shp`、`.shx`、`.dbf` 和 `.prj` 的 ZIP 文件，也可以同时选择这些配套文件。必须提供 `.prj` 文件，以便将边界转换为 WGS84；上传的文件会保存在新区域的媒体目录中。

如需 MySQL，请编辑 `.env` 中的 MySQL 配置，提前创建空数据库 `fieldmoist`，并确认 MySQL 服务已启动。

## 3. 配置前端地图

```powershell
Copy-Item frontend/.env.example frontend/.env
```

编辑 `frontend/.env`，设置 `VITE_AMAP_KEY` 与 `VITE_AMAP_SECURITY_CODE`。发布时应在高德控制台限制允许使用这些凭据的域名。

## 4. 放置并注册数据

本地项目要求以下目录：

```text
backend/media/images/83/shp/shp.shp
backend/media/images/83/2018-05-01_2018-05-24/soil_moisture_result/*.tif
backend/media/images/83/2018-05-01_2018-05-24/soil_moisture_png/*.png
```

TIF 和 PNG 应分别为 24 个逐日文件。随后运行：

```powershell
python backend/manage.py migrate
python backend/manage.py validate_fieldmoist_data --dataset all
python backend/manage.py seed_fieldmoist
python backend/manage.py check
```

初始化命令读取现有简化 SHP 并注册 jiefangzha，不删除其他研究区。
配套数据还应包含 `test` 输入，完整清单见 [数据目录说明](backend/media/README.md)。

## 5. 安装前端依赖

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
```

## 6. 启动系统

后端 PowerShell 窗口：

```powershell
conda activate FieldMoist
python backend/manage.py runserver 0.0.0.0:8000
```

前端 PowerShell 窗口：

```powershell
npm run dev --prefix frontend
```

本机访问 `http://localhost:5173`，后端健康检查地址为 `http://localhost:8000/api/health/`。

## 常见问题

- PowerShell 提示不能加载 `npm.ps1`：执行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 后重开 PowerShell，或使用 `npm.cmd`。
- 底图空白：检查两个高德环境变量及域名白名单，修改后重启 Vite。
- Explore 页面默认使用原 SoilMoisturePlatform 的高德卫星底图，可通过地图右上角的 Satellite / Standard 开关自由切换。
- 高德底图瓦片首次使用后会保存到浏览器的 `FieldMoist AMap tiles` 缓存。在 `localhost` 或 HTTPS 下由内置 Service Worker 管理；通过不安全的局域网 HTTP 地址访问时，浏览器可能只使用普通 HTTP 缓存，这是浏览器对 Service Worker 的安全限制。
- 数据文件缺失：运行 `python backend/manage.py validate_fieldmoist_data --dataset all`，按报告补齐输入。
- 核心模块加载失败：确认使用 Windows x64 和 Python 3.12，使用 `tools/install_core.py` 安装匹配版本的私有编译文件。
- GDAL 导入失败：重新创建 Conda 环境，避免混用不同来源的 GDAL 动态库。
- NASA POWER 优先读取已缓存的网格数据，只有缓存缺失时才需要网络；本地逐日影像浏览不受影响。高德不可用时仍可显示土壤水分产品，只是不显示底图。
- 如需离线查看底图，请在联网时打开目标区域，分别切换 Satellite 和 Standard，并浏览需要的区域与缩放级别。离线只能显示已经浏览过的瓦片；后端接口和未缓存的逐日产品仍需要网络。


## 首次启动与网络说明

推荐新建名为 `FieldMoist` 的 Conda 环境；`SoilMoisturePlatform` 是旧环境名。在线模式首次使用前，在 `.env` 设置 `EARTH_ENGINE_PROJECT`，运行 `python tools/authorize_earth_engine.py` 完成 GEE 首次认证。认证和在线下载需要能够访问 Google Earth Engine 的网络；中国境内网络可能无法连接 GEE，请使用离线模式或配置允许的网络出口。

数据包解压后先运行 `python backend/manage.py validate_fieldmoist_data --dataset all`。网页中选择 Offline，输入 `test`，等待测试预设加载并点击“开始处理”，该流程只使用本地测试数据。
# PNG 展示与 test 重算

彩色 PNG 通过本地服务直接显示，不依赖高德瓦片或 ImageLayer。高德不可用时仍可查看已有产品。
每次启动离线 `test` 均清理该测试的预处理副本、周期缓存、完成标记和旧 TIF/PNG，再从原始输入运行；保留输入、共享模型和 NASA 缓存。
更新程序后重启前后端即可，无需删除数据库或重新登记 83。

选点圆圈显示在彩色 PNG 上方；高德脚本不可用时也可在本地产品上选点。后台每个计算阶段仅显示简短提示，不再显示逐文件进度和算法细节。默认不生成 `ml_patch_report.xlsx`，测站 Excel 输入和土壤水分计算仍正常执行。
