# 基于模拟数据的校园生活服务设施可达性与优化分析

## 项目简介

本项目是一个基于 GeoPandas 的空间分析练习项目，用于演示校园生活服务设施可达性与新增服务设施优化选址的完整流程。

## 重要声明：本项目基于模拟数据

本项目使用模拟校园生活点、模拟 POI 和模拟候选点数据。所有距离、指数、短板识别和选址建议均用于方法训练和流程演示，不应被解释为真实校园设施规划结论。

## 项目功能

- 构建模拟校园生活点、模拟 POI 和模拟候选点数据
- 将普通表格转换为 GeoDataFrame
- 统一坐标系，并转换为 EPSG:3857 米制坐标系
- 构建 500 米生活圈缓冲区
- 使用 `sjoin` 判断 POI 是否落入生活圈
- 统计每个生活点周边不同类型 POI 数量
- 计算生活便利度指数
- 计算生活点到关键设施的最近距离
- 通过反向标准化计算可达性得分
- 构建综合可达性指数
- 自动识别主要短板设施并生成优化建议
- 设置新增服务设施候选点并进行选址评分
- 导出 CSV、GeoJSON、PNG 图片、Markdown 报告和 README

## 技术栈

Python、pandas、GeoPandas、Shapely、pyproj、matplotlib。

## 项目结构

```text
campus_service_project/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ src/
│  └─ campus_service_analysis.py
├─ outputs/
│  ├─ tables/
│  ├─ geojson/
│  ├─ figures/
│  └─ reports/
└─ docs/
   └─ project_report.md
```

## 运行环境

建议使用 Python 3.10 及以上版本。当前项目可在 Windows PowerShell 中运行。

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 运行方式

```powershell
cd D:\python_data_learning\projects\campus_service_project
D:\python_data_learning\.venv\Scripts\python.exe .\src\campus_service_analysis.py
```

## 输出结果说明

- `outputs/tables/`：CSV 表格结果，编码为 `utf-8-sig`
- `outputs/geojson/`：空间分析 GeoJSON 结果
- `outputs/figures/`：PNG 可视化图片
- `outputs/reports/`：自动生成的 Markdown 报告
- `docs/project_report.md`：报告副本，便于项目展示

## 核心方法说明

项目在 EPSG:3857 坐标系下进行缓冲区和距离计算。生活圈覆盖分析使用 500 米缓冲区和空间连接；可达性分析使用最近距离、反向 Min-Max 标准化和加权求和；选址模拟使用需求权重、加权平均服务距离、覆盖生活点数量和综合选址得分。

## 项目结果摘要

- 综合可达性最高生活点：图书馆，指数 0.750
- 综合可达性最低生活点：体育场，指数 0.291
- 最常见主要短板设施：公交站，出现 4 次
- 新增自助打印点最优候选点：图书馆候选点
- 最优候选点综合选址得分：1.000
- 最优候选点加权平均服务距离：354.968 米

## 不足与后续改进

本项目没有使用真实校园数据，也没有使用道路网络距离。后续可接入真实 POI、实地采集数据和道路网络，计算真实步行距离或步行时间，并通过问卷或层次分析法校准指标权重。

## 简历描述参考

完成“基于模拟数据的校园生活服务设施可达性与优化分析”项目，使用 GeoPandas 构建生活点与 POI 空间数据，完成 500 米生活圈覆盖、空间连接、最近设施距离、反向标准化、综合可达性指数、服务短板识别和候选点选址评分，并自动导出 CSV、GeoJSON、PNG 和 Markdown 报告。
