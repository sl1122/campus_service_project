"""
基于模拟数据的校园生活服务设施可达性与优化分析。

本脚本使用模拟校园生活点、模拟 POI 和模拟候选点数据，完成生活圈覆盖、
关键设施可达性、服务短板识别和新增服务设施候选点选址评分。分析结果仅用于
GeoPandas 方法训练和流程演示，不代表真实校园设施规划结论。
"""

from pathlib import Path
import shutil
import warnings

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
GEOJSON_DIR = OUTPUT_DIR / "geojson"
FIGURE_DIR = OUTPUT_DIR / "figures"
REPORT_DIR = OUTPUT_DIR / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"

SOURCE_CRS = "EPSG:4326"
PROJECTED_CRS = "EPSG:3857"


def ensure_output_dirs() -> None:
    """创建标准输出目录。"""
    for path in [TABLE_DIR, GEOJSON_DIR, FIGURE_DIR, REPORT_DIR, DOCS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def setup_matplotlib() -> None:
    """设置 Matplotlib 中文字体，字体不可用时不让程序崩溃。"""
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    warnings.filterwarnings("ignore", message="Glyph .* missing from font.*")


def make_point_gdf(
    df: pd.DataFrame,
    x_col: str = "经度",
    y_col: str = "纬度",
    crs: str = SOURCE_CRS,
) -> gpd.GeoDataFrame:
    """将包含经纬度字段的普通表格转换为点状 GeoDataFrame。"""
    return gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df[x_col], df[y_col]),
        crs=crs,
    )


def reverse_min_max_normalize(series: pd.Series) -> pd.Series:
    """反向 Min-Max 标准化：数值越小得分越高，适合距离类指标。"""
    max_value = series.max()
    min_value = series.min()
    if max_value == min_value:
        return pd.Series(1.0, index=series.index)
    return (max_value - series) / (max_value - min_value)


def min_max_normalize(series: pd.Series) -> pd.Series:
    """正向 Min-Max 标准化：数值越大得分越高。"""
    max_value = series.max()
    min_value = series.min()
    if max_value == min_value:
        return pd.Series(1.0, index=series.index)
    return (series - min_value) / (max_value - min_value)


def save_table(df: pd.DataFrame, file_name: str) -> Path:
    """按 utf-8-sig 编码导出 CSV，便于 Excel 打开中文。"""
    path = TABLE_DIR / file_name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def save_geojson(gdf: gpd.GeoDataFrame, file_name: str) -> Path:
    """导出 GeoJSON；统一转回 EPSG:4326，便于 GIS 和网页地图查看。"""
    path = GEOJSON_DIR / file_name
    output_gdf = gdf.to_crs(SOURCE_CRS)
    output_gdf.to_file(path, driver="GeoJSON")
    return path


def save_current_figure(file_name: str) -> Path:
    """保存当前图片并关闭画布。"""
    path = FIGURE_DIR / file_name
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    return path


def add_point_labels(ax, gdf: gpd.GeoDataFrame, label_col: str, fontsize: int = 8) -> None:
    """为点图层添加标签。"""
    for _, row in gdf.iterrows():
        ax.annotate(
            row[label_col],
            xy=(row.geometry.x, row.geometry.y),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=fontsize,
        )


def build_mock_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """构建模拟校园生活点、模拟 POI 和模拟候选点数据。"""
    life_df = pd.DataFrame(
        {
            "生活点名称": ["图书馆", "一号宿舍区", "二号宿舍区", "教学楼群", "东校门", "体育场"],
            "生活点类型": ["学习", "居住", "居住", "教学", "出入口", "运动"],
            "经度": [111.6900, 111.6865, 111.6935, 111.6910, 111.6960, 111.6880],
            "纬度": [29.0550, 29.0565, 29.0525, 29.0570, 29.0555, 29.0515],
        }
    )

    poi_df = pd.DataFrame(
        {
            "POI名称": [
                "一食堂",
                "二食堂",
                "校外小吃街",
                "校园超市",
                "东门便利店",
                "水果店",
                "校医院",
                "东门药店",
                "东门公交站",
                "南门公交站",
                "菜鸟驿站",
                "宿舍快递点",
                "图文打印店",
                "教学楼打印点",
                "奶茶店A",
                "奶茶店B",
                "咖啡店",
            ],
            "POI类型": [
                "食堂",
                "食堂",
                "餐饮",
                "超市",
                "超市",
                "超市",
                "医疗",
                "医疗",
                "公交站",
                "公交站",
                "快递点",
                "快递点",
                "打印店",
                "打印店",
                "饮品",
                "饮品",
                "饮品",
            ],
            "经度": [
                111.6890,
                111.6920,
                111.6970,
                111.6870,
                111.6965,
                111.6945,
                111.6905,
                111.6972,
                111.6968,
                111.6885,
                111.6868,
                111.6938,
                111.6902,
                111.6915,
                111.6955,
                111.6875,
                111.6928,
            ],
            "纬度": [
                29.0545,
                29.0528,
                29.0558,
                29.0568,
                29.0552,
                29.0530,
                29.0558,
                29.0560,
                29.0556,
                29.0508,
                29.0562,
                29.0520,
                29.0553,
                29.0572,
                29.0550,
                29.0560,
                29.0535,
            ],
        }
    )

    candidate_df = pd.DataFrame(
        {
            "候选点名称": ["图书馆候选点", "教学楼候选点", "宿舍区候选点", "东校门候选点", "体育场候选点"],
            "候选点类型": ["学习服务", "教学服务", "生活服务", "出入口服务", "运动服务"],
            "经度": [111.6903, 111.6912, 111.6870, 111.6962, 111.6882],
            "纬度": [29.0552, 29.0571, 29.0563, 29.0554, 29.0518],
        }
    )

    life_gdf = make_point_gdf(life_df)
    poi_gdf = make_point_gdf(poi_df)
    candidate_gdf = make_point_gdf(candidate_df)
    return life_gdf, poi_gdf, candidate_gdf


def get_nearest_poi_distance(
    life_gdf_projected: gpd.GeoDataFrame,
    poi_gdf_projected: gpd.GeoDataFrame,
    poi_type: str,
) -> pd.DataFrame:
    """计算每个生活点到指定 POI 类型的最近设施和最近距离。"""
    target_poi = poi_gdf_projected[poi_gdf_projected["POI类型"] == poi_type].copy()
    if target_poi.empty:
        raise ValueError(f"模拟 POI 数据中不存在 POI 类型：{poi_type}")

    records = []
    for _, life_row in life_gdf_projected.iterrows():
        temp_poi = target_poi.copy()
        temp_poi["距离_m"] = temp_poi.distance(life_row.geometry)
        nearest_poi = temp_poi.sort_values("距离_m").iloc[0]
        records.append(
            {
                "生活点名称": life_row["生活点名称"],
                "生活点类型": life_row["生活点类型"],
                f"最近{poi_type}": nearest_poi["POI名称"],
                f"最近{poi_type}距离_m": nearest_poi["距离_m"],
            }
        )
    return pd.DataFrame(records)


def generate_suggestion(row: pd.Series) -> str:
    """根据主要短板设施自动生成优化建议。"""
    life_name = row["生活点名称"]
    shortboard = row["主要短板设施"]
    distance = row["最大短板距离_m"]

    suggestion_map = {
        "食堂": f"{life_name}周边餐饮服务可达性相对不足，最近食堂距离约{distance:.0f}米，建议优化就餐步行路径或补充临时餐饮服务点。",
        "超市": f"{life_name}周边日常购物便利性相对不足，最近超市距离约{distance:.0f}米，建议增设便利店、自助售货点或优化校园超市布局。",
        "医疗": f"{life_name}周边医疗服务可达性相对不足，最近医疗点距离约{distance:.0f}米，建议完善应急医疗点、急救箱或校医院指引标识。",
        "公交站": f"{life_name}周边交通接驳便利性相对不足，最近公交站距离约{distance:.0f}米，建议优化校门、道路与公交站之间的步行路径。",
        "打印店": f"{life_name}周边学习配套服务相对不足，最近打印点距离约{distance:.0f}米，建议在教学或学习空间附近补充自助打印设备。",
    }
    return suggestion_map.get(
        shortboard,
        f"{life_name}周边存在一定服务短板，建议结合实际需求进一步优化设施布局。",
    )


def analyze_life_circle(
    life_projected: gpd.GeoDataFrame,
    poi_projected: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """构建 500 米生活圈，统计生活圈内 POI 类型数量并计算便利度指数。"""
    life_buffer_gdf = life_projected.copy()
    life_buffer_gdf["geometry"] = life_projected.buffer(500)

    life_buffer_for_join = life_buffer_gdf[["生活点名称", "生活点类型", "geometry"]].copy()
    poi_life_joined = gpd.sjoin(
        poi_projected,
        life_buffer_for_join,
        how="left",
        predicate="within",
    )
    poi_in_life_circle = poi_life_joined.dropna(subset=["生活点名称"])

    life_poi_count = (
        poi_in_life_circle.groupby(["生活点名称", "POI类型"])
        .size()
        .reset_index(name="数量")
    )
    life_poi_table = (
        life_poi_count.pivot_table(
            index="生活点名称",
            columns="POI类型",
            values="数量",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(columns=None)
    )

    life_service_result = life_buffer_for_join.merge(
        life_poi_table,
        on="生活点名称",
        how="left",
    )
    poi_cols = ["食堂", "餐饮", "超市", "医疗", "公交站", "快递点", "打印店", "饮品"]
    for col in poi_cols:
        if col not in life_service_result.columns:
            life_service_result[col] = 0
    life_service_result[poi_cols] = life_service_result[poi_cols].fillna(0).astype(int)
    life_service_result["POI总数"] = life_service_result[poi_cols].sum(axis=1)

    life_service_weights = {
        "食堂": 1.5,
        "餐饮": 1.2,
        "超市": 1.3,
        "医疗": 1.5,
        "公交站": 1.4,
        "快递点": 1.1,
        "打印店": 1.0,
        "饮品": 0.8,
    }
    life_service_result["生活便利度指数"] = sum(
        life_service_result[col] * weight
        for col, weight in life_service_weights.items()
    )

    life_service_summary = life_service_result[
        ["生活点名称", "生活点类型", *poi_cols, "POI总数", "生活便利度指数", "geometry"]
    ].sort_values("生活便利度指数", ascending=False)

    return poi_life_joined, life_service_result, life_service_summary


def analyze_accessibility(
    life_projected: gpd.GeoDataFrame,
    poi_projected: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, gpd.GeoDataFrame, pd.DataFrame, list[str]]:
    """计算关键设施最近距离、反向标准化得分和综合可达性指数。"""
    key_poi_types = ["食堂", "超市", "医疗", "公交站", "打印店"]
    nearest_poi_tables = {
        poi_type: get_nearest_poi_distance(life_projected, poi_projected, poi_type)
        for poi_type in key_poi_types
    }

    accessibility_result = life_projected[["生活点名称", "生活点类型"]].copy()
    for poi_type, nearest_df in nearest_poi_tables.items():
        keep_cols = ["生活点名称", f"最近{poi_type}", f"最近{poi_type}距离_m"]
        accessibility_result = accessibility_result.merge(
            nearest_df[keep_cols],
            on="生活点名称",
            how="left",
        )

    accessibility_distance_cols = [f"最近{poi_type}距离_m" for poi_type in key_poi_types]
    for poi_type in key_poi_types:
        distance_col = f"最近{poi_type}距离_m"
        score_col = f"{poi_type}可达性得分"
        accessibility_result[score_col] = reverse_min_max_normalize(
            accessibility_result[distance_col]
        )

    accessibility_weights = {
        "食堂": 0.25,
        "超市": 0.20,
        "医疗": 0.20,
        "公交站": 0.20,
        "打印店": 0.15,
    }
    accessibility_result["综合可达性指数"] = sum(
        accessibility_result[f"{poi_type}可达性得分"] * weight
        for poi_type, weight in accessibility_weights.items()
    )

    life_accessibility_gdf = life_projected.merge(
        accessibility_result.drop(columns=["生活点类型"]),
        on="生活点名称",
        how="left",
    )

    final_accessibility_table = life_accessibility_gdf[
        ["生活点名称", "生活点类型", "综合可达性指数", *accessibility_distance_cols]
    ].copy()
    final_accessibility_table["综合可达性指数"] = final_accessibility_table[
        "综合可达性指数"
    ].round(3)
    for col in accessibility_distance_cols:
        final_accessibility_table[col] = final_accessibility_table[col].round(2)
    final_accessibility_table = final_accessibility_table.sort_values(
        "综合可达性指数",
        ascending=False,
    )

    return (
        accessibility_result,
        life_accessibility_gdf,
        final_accessibility_table,
        accessibility_distance_cols,
    )


def identify_shortboards(
    life_accessibility_gdf: gpd.GeoDataFrame,
    accessibility_distance_cols: list[str],
) -> tuple[gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:
    """识别主要短板设施并生成优化建议。"""
    result_gdf = life_accessibility_gdf.copy()
    result_gdf["可达性等级"] = pd.cut(
        result_gdf["综合可达性指数"],
        bins=[-0.001, 0.4, 0.6, 0.8, 1.0],
        labels=["较低", "中等", "较高", "高"],
        include_lowest=True,
    ).astype(str)
    result_gdf["最大短板距离_m"] = result_gdf[accessibility_distance_cols].max(axis=1)
    result_gdf["最大短板字段"] = result_gdf[accessibility_distance_cols].idxmax(axis=1)

    shortboard_map = {
        "最近食堂距离_m": "食堂",
        "最近超市距离_m": "超市",
        "最近医疗距离_m": "医疗",
        "最近公交站距离_m": "公交站",
        "最近打印店距离_m": "打印店",
    }
    result_gdf["主要短板设施"] = result_gdf["最大短板字段"].map(shortboard_map)
    result_gdf["优化建议"] = result_gdf.apply(generate_suggestion, axis=1)

    final_shortboard_result = result_gdf[
        [
            "生活点名称",
            "生活点类型",
            "综合可达性指数",
            "可达性等级",
            "主要短板设施",
            "最大短板距离_m",
            "优化建议",
        ]
    ].copy()
    final_shortboard_result["综合可达性指数"] = final_shortboard_result[
        "综合可达性指数"
    ].round(3)
    final_shortboard_result["最大短板距离_m"] = final_shortboard_result[
        "最大短板距离_m"
    ].round(2)
    final_shortboard_result = final_shortboard_result.sort_values(
        "综合可达性指数",
        ascending=True,
    )

    shortboard_count = (
        final_shortboard_result["主要短板设施"]
        .value_counts()
        .rename_axis("主要短板设施")
        .reset_index(name="出现次数")
    )
    return result_gdf, final_shortboard_result, shortboard_count


def score_candidates(
    life_accessibility_gdf: gpd.GeoDataFrame,
    candidate_projected: gpd.GeoDataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    """基于需求权重、距离得分和覆盖得分进行候选点选址评分。"""
    candidate_distance_records = []
    for _, candidate_row in candidate_projected.iterrows():
        for _, life_row in life_accessibility_gdf.iterrows():
            candidate_distance_records.append(
                {
                    "候选点名称": candidate_row["候选点名称"],
                    "候选点类型": candidate_row["候选点类型"],
                    "生活点名称": life_row["生活点名称"],
                    "生活点类型": life_row["生活点类型"],
                    "距离_m": candidate_row.geometry.distance(life_row.geometry),
                }
            )
    candidate_distance_df = pd.DataFrame(candidate_distance_records)

    demand_weights_map = {
        "学习": 1.5,
        "教学": 1.5,
        "居住": 1.2,
        "出入口": 0.8,
        "运动": 0.7,
    }
    candidate_distance_df["生活点需求权重"] = candidate_distance_df["生活点类型"].map(
        demand_weights_map
    )

    candidate_score_records = []
    for candidate_name, temp_df in candidate_distance_df.groupby("候选点名称"):
        weighted_avg_distance = (
            (temp_df["距离_m"] * temp_df["生活点需求权重"]).sum()
            / temp_df["生活点需求权重"].sum()
        )
        covered_300m_count = (temp_df["距离_m"] <= 300).sum()
        covered_500m_count = (temp_df["距离_m"] <= 500).sum()
        candidate_score_records.append(
            {
                "候选点名称": candidate_name,
                "加权平均服务距离_m": weighted_avg_distance,
                "300米覆盖生活点数": covered_300m_count,
                "500米覆盖生活点数": covered_500m_count,
            }
        )

    candidate_scores_df = pd.DataFrame(candidate_score_records)
    candidate_scores_df["距离得分"] = reverse_min_max_normalize(
        candidate_scores_df["加权平均服务距离_m"]
    )
    max_coverage = candidate_scores_df["500米覆盖生活点数"].max()
    if max_coverage == 0:
        candidate_scores_df["覆盖得分"] = 0.0
    else:
        candidate_scores_df["覆盖得分"] = (
            candidate_scores_df["500米覆盖生活点数"] / max_coverage
        )
    candidate_scores_df["综合选址得分"] = (
        candidate_scores_df["距离得分"] * 0.7
        + candidate_scores_df["覆盖得分"] * 0.3
    )
    candidate_scores_df = candidate_scores_df.sort_values(
        "综合选址得分",
        ascending=False,
    )

    for col in ["加权平均服务距离_m", "距离得分", "覆盖得分", "综合选址得分"]:
        candidate_scores_df[col] = candidate_scores_df[col].round(3)

    best_candidate = candidate_scores_df.head(1).copy()
    candidate_score_gdf = candidate_projected.merge(
        candidate_scores_df,
        on="候选点名称",
        how="left",
    )

    return candidate_distance_df, candidate_scores_df, best_candidate, candidate_score_gdf


def create_figures(
    life_projected: gpd.GeoDataFrame,
    poi_projected: gpd.GeoDataFrame,
    life_service_result: gpd.GeoDataFrame,
    life_accessibility_gdf: gpd.GeoDataFrame,
    candidate_score_gdf: gpd.GeoDataFrame,
    candidate_scores_df: pd.DataFrame,
) -> list[Path]:
    """生成项目 PNG 图片。"""
    figure_paths = []

    fig, ax = plt.subplots(figsize=(9, 7))
    poi_projected.plot(ax=ax, column="POI类型", legend=True, markersize=38, alpha=0.8)
    life_projected.plot(ax=ax, color="#d62728", markersize=80, marker="*", label="生活点")
    add_point_labels(ax, life_projected, "生活点名称")
    ax.set_title("校园生活点与周边 POI 分布图")
    ax.set_axis_off()
    ax.legend(loc="upper left")
    figure_paths.append(save_current_figure("campus_poi_distribution.png"))

    fig, ax = plt.subplots(figsize=(9, 7))
    life_service_result.boundary.plot(ax=ax, color="#4c78a8", linewidth=1.2)
    life_service_result.plot(ax=ax, color="#9ecae1", alpha=0.25)
    poi_projected.plot(ax=ax, column="POI类型", legend=True, markersize=34, alpha=0.75)
    life_projected.plot(ax=ax, color="#d62728", markersize=70, marker="*")
    add_point_labels(ax, life_projected, "生活点名称")
    ax.set_title("校园生活点 500 米生活圈与 POI 分布图")
    ax.set_axis_off()
    figure_paths.append(save_current_figure("life_circle_500m.png"))

    fig, ax = plt.subplots(figsize=(9, 7))
    life_service_result.plot(
        ax=ax,
        column="生活便利度指数",
        cmap="YlGnBu",
        legend=True,
        edgecolor="#555555",
        linewidth=0.8,
        alpha=0.75,
    )
    life_projected.plot(ax=ax, color="#d62728", markersize=65, marker="*")
    add_point_labels(ax, life_projected, "生活点名称")
    ax.set_title("校园生活圈便利度指数空间分布图")
    ax.set_axis_off()
    figure_paths.append(save_current_figure("convenience_index_map.png"))

    fig, ax = plt.subplots(figsize=(9, 7))
    life_accessibility_gdf.plot(
        ax=ax,
        column="综合可达性指数",
        cmap="viridis",
        legend=True,
        markersize=160,
        edgecolor="black",
        linewidth=0.6,
    )
    add_point_labels(ax, life_accessibility_gdf, "生活点名称")
    ax.set_title("校园生活点综合可达性空间分布图")
    ax.set_axis_off()
    figure_paths.append(save_current_figure("accessibility_index_map.png"))

    fig, ax = plt.subplots(figsize=(9, 7))
    life_projected.plot(ax=ax, color="#d62728", markersize=70, marker="*", label="生活点")
    candidate_score_gdf.plot(
        ax=ax,
        column="综合选址得分",
        cmap="plasma",
        legend=True,
        markersize=130,
        edgecolor="black",
        linewidth=0.6,
        label="候选点",
    )
    add_point_labels(ax, life_projected, "生活点名称")
    add_point_labels(ax, candidate_score_gdf, "候选点名称")
    ax.set_title("新增服务设施候选点分布图")
    ax.set_axis_off()
    ax.legend(loc="upper left")
    figure_paths.append(save_current_figure("candidate_points_map.png"))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bar_df = candidate_scores_df.sort_values("综合选址得分", ascending=True)
    ax.barh(bar_df["候选点名称"], bar_df["综合选址得分"], color="#4c78a8")
    ax.set_xlabel("综合选址得分")
    ax.set_title("新增服务设施候选点评分结果")
    ax.set_xlim(0, max(1.0, float(candidate_scores_df["综合选址得分"].max()) + 0.05))
    for index, value in enumerate(bar_df["综合选址得分"]):
        ax.text(value + 0.01, index, f"{value:.3f}", va="center", fontsize=9)
    figure_paths.append(save_current_figure("candidate_score_bar.png"))

    return figure_paths


def create_report(
    final_accessibility_table: pd.DataFrame,
    final_shortboard_result: pd.DataFrame,
    shortboard_count: pd.DataFrame,
    candidate_scores_df: pd.DataFrame,
    best_candidate: pd.DataFrame,
) -> tuple[Path, Path]:
    """生成 Markdown 报告，并复制一份到 docs/project_report.md。"""
    highest_accessibility = final_accessibility_table.iloc[0]
    lowest_accessibility = final_accessibility_table.iloc[-1]
    most_common_shortboard = shortboard_count.iloc[0]
    best_row = best_candidate.iloc[0]

    report_text = f"""# 基于模拟数据的校园生活服务设施可达性与优化分析

## 1. 研究背景

本项目围绕校园生活服务设施的空间覆盖与可达性评价展开，目标是演示如何使用 GeoPandas 完成点数据构建、坐标系转换、缓冲区、空间连接、距离计算、指标标准化和候选点选址评分等流程。

**重要声明：本项目使用模拟校园生活点、模拟 POI 和模拟候选点数据，结果用于方法训练和流程演示，不应被解释为真实校园设施规划结论。**

## 2. 数据说明

本项目数据全部为模拟数据。模拟校园生活点包括图书馆、宿舍区、教学楼群、东校门和体育场等；模拟 POI 包括食堂、餐饮、超市、医疗、公交站、快递点、打印店和饮品店等；模拟候选点用于演示新增自助打印点的优化选址。

所有点数据先以 EPSG:4326 经纬度坐标系构建，再统一转换为 EPSG:3857 米制投影坐标系。报告中的距离均为基于 EPSG:3857 的平面直线距离，不等同于真实步行距离或道路网络距离。

## 3. 研究方法

项目首先构建 500 米生活圈缓冲区，并使用 `sjoin` 判断模拟 POI 是否落入各生活圈；随后统计每个生活点周边不同类型 POI 数量，并按设施权重计算生活便利度指数。

关键设施可达性分析中，项目计算每个生活点到食堂、超市、医疗、公交站和打印店的最近距离。由于距离越短代表可达性越好，项目通过反向标准化计算各类设施可达性得分，并加权形成综合可达性指数。

在短板识别中，项目将每个生活点最近距离最大的关键设施作为主要短板设施，并自动生成优化建议。新增服务设施选址模拟中，项目计算候选点到生活点距离，结合需求权重、距离得分和覆盖得分，输出最优候选点。

## 4. 生活圈设施覆盖分析

500 米生活圈分析显示，不同模拟生活点周边 POI 数量和类型存在差异。生活便利度指数越高，说明该生活点 500 米范围内模拟服务设施的数量和类型越丰富。

## 5. 关键设施可达性分析

本次模拟结果中，综合可达性最高的生活点为 **{highest_accessibility['生活点名称']}**，综合可达性指数为 **{highest_accessibility['综合可达性指数']:.3f}**；综合可达性最低的生活点为 **{lowest_accessibility['生活点名称']}**，综合可达性指数为 **{lowest_accessibility['综合可达性指数']:.3f}**。

## 6. 校园生活服务短板识别与优化建议

项目通过比较每个生活点到不同关键设施的最近距离，识别主要短板设施。本次模拟中，最常见的主要短板设施为 **{most_common_shortboard['主要短板设施']}**，出现 **{int(most_common_shortboard['出现次数'])}** 次。

短板识别结果已自动生成逐生活点优化建议，例如补充自助打印设备、完善医疗应急点、优化公交接驳步行路径或增强日常购物服务等。上述建议仍然基于模拟数据，仅用于展示从空间分析结果转化为规划建议文本的流程。

## 7. 新增服务设施优化选址模拟

项目以新增自助打印点为例设置多个候选点，计算候选点到各生活点的 EPSG:3857 平面直线距离，并结合不同生活点对打印服务的需求权重进行评分。

本次模拟中，新增自助打印点最优候选点为 **{best_row['候选点名称']}**；最优候选点综合选址得分为 **{best_row['综合选址得分']:.3f}**；最优候选点加权平均服务距离为 **{best_row['加权平均服务距离_m']:.3f} 米**。

## 8. 主要结论

第一，基于模拟数据的 500 米生活圈分析可以展示不同生活点周边服务设施覆盖差异。

第二，最近距离和综合可达性指数可以补充单纯设施数量统计的不足，更直观地比较生活点到关键设施的接近程度。

第三，短板识别与自动建议生成可以把“哪里不方便”转化为“优先优化什么设施”的结构化结果。

第四，候选点评分方法可以用于演示新增服务设施的选址比较，但评分结果依赖模拟位置、经验权重和距离阈值设置。

## 9. 不足与改进方向

本项目使用模拟数据，不代表任何真实校园的设施现状。距离为基于 EPSG:3857 的平面直线距离，未考虑道路、建筑、围墙、出入口和真实步行路径。综合可达性指数和选址评分中的权重为经验设定，具有主观性。

后续如用于真实研究，应接入实地采集数据、真实 POI、道路网络和行人通行路径，并通过问卷、访谈或层次分析法等方式校准权重。当前结果仅适合作为 GeoPandas 空间分析方法训练和项目流程展示。
"""

    report_path = REPORT_DIR / "校园生活服务设施可达性与优化分析报告.md"
    report_path.write_text(report_text, encoding="utf-8")
    docs_report_path = DOCS_DIR / "project_report.md"
    shutil.copyfile(report_path, docs_report_path)
    return report_path, docs_report_path


def create_readme(
    final_accessibility_table: pd.DataFrame,
    shortboard_count: pd.DataFrame,
    best_candidate: pd.DataFrame,
) -> Path:
    """生成项目 README。"""
    highest_accessibility = final_accessibility_table.iloc[0]
    lowest_accessibility = final_accessibility_table.iloc[-1]
    most_common_shortboard = shortboard_count.iloc[0]
    best_row = best_candidate.iloc[0]

    readme_text = f"""# 基于模拟数据的校园生活服务设施可达性与优化分析

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
cd D:\\python_data_learning\\projects\\campus_service_project
D:\\python_data_learning\\.venv\\Scripts\\python.exe .\\src\\campus_service_analysis.py
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

- 综合可达性最高生活点：{highest_accessibility['生活点名称']}，指数 {highest_accessibility['综合可达性指数']:.3f}
- 综合可达性最低生活点：{lowest_accessibility['生活点名称']}，指数 {lowest_accessibility['综合可达性指数']:.3f}
- 最常见主要短板设施：{most_common_shortboard['主要短板设施']}，出现 {int(most_common_shortboard['出现次数'])} 次
- 新增自助打印点最优候选点：{best_row['候选点名称']}
- 最优候选点综合选址得分：{best_row['综合选址得分']:.3f}
- 最优候选点加权平均服务距离：{best_row['加权平均服务距离_m']:.3f} 米

## 不足与后续改进

本项目没有使用真实校园数据，也没有使用道路网络距离。后续可接入真实 POI、实地采集数据和道路网络，计算真实步行距离或步行时间，并通过问卷或层次分析法校准指标权重。

## 简历描述参考

完成“基于模拟数据的校园生活服务设施可达性与优化分析”项目，使用 GeoPandas 构建生活点与 POI 空间数据，完成 500 米生活圈覆盖、空间连接、最近设施距离、反向标准化、综合可达性指数、服务短板识别和候选点选址评分，并自动导出 CSV、GeoJSON、PNG 和 Markdown 报告。
"""

    readme_path = PROJECT_ROOT / "README.md"
    readme_path.write_text(readme_text, encoding="utf-8")
    return readme_path


def create_project_summary(
    table_paths: list[Path],
    geojson_paths: list[Path],
    figure_paths: list[Path],
    report_paths: list[Path],
) -> pd.DataFrame:
    """生成项目成果清单。"""
    records = []
    for category, paths in [
        ("CSV表格", table_paths),
        ("GeoJSON空间数据", geojson_paths),
        ("PNG图片", figure_paths),
        ("Markdown报告", report_paths),
    ]:
        for path in paths:
            records.append(
                {
                    "成果类型": category,
                    "文件名称": path.name,
                    "相对路径": str(path.relative_to(PROJECT_ROOT)),
                    "说明": "基于模拟数据自动生成",
                }
            )
    return pd.DataFrame(records)


def main() -> None:
    """项目主流程：模拟数据构建、空间分析、选址评分和成果导出。"""
    ensure_output_dirs()
    setup_matplotlib()

    life_gdf, poi_gdf, candidate_gdf = build_mock_data()
    life_projected = life_gdf.to_crs(PROJECTED_CRS)
    poi_projected = poi_gdf.to_crs(PROJECTED_CRS)
    candidate_projected = candidate_gdf.to_crs(PROJECTED_CRS)

    poi_life_joined, life_service_result, life_service_summary = analyze_life_circle(
        life_projected,
        poi_projected,
    )
    (
        accessibility_result,
        life_accessibility_gdf,
        final_accessibility_table,
        accessibility_distance_cols,
    ) = analyze_accessibility(life_projected, poi_projected)
    (
        shortboard_gdf,
        final_shortboard_result,
        shortboard_count,
    ) = identify_shortboards(life_accessibility_gdf, accessibility_distance_cols)
    (
        candidate_distance_df,
        candidate_scores_df,
        best_candidate,
        candidate_score_gdf,
    ) = score_candidates(shortboard_gdf, candidate_projected)

    figure_paths = create_figures(
        life_projected,
        poi_projected,
        life_service_result,
        life_accessibility_gdf,
        candidate_score_gdf,
        candidate_scores_df,
    )

    geojson_paths = [
        save_geojson(poi_life_joined, "POI点_校园生活圈空间连接结果.geojson"),
        save_geojson(life_service_result, "校园生活圈便利度统计结果.geojson"),
        save_geojson(life_accessibility_gdf, "校园生活点综合可达性分析结果.geojson"),
        save_geojson(shortboard_gdf, "校园生活服务短板识别与优化建议.geojson"),
        save_geojson(candidate_score_gdf, "新增服务设施候选点.geojson"),
    ]

    table_paths = [
        save_table(
            life_service_summary.drop(columns="geometry"),
            "校园生活圈便利度统计结果.csv",
        ),
        save_table(final_accessibility_table, "校园生活点综合可达性分析结果.csv"),
        save_table(final_shortboard_result, "校园生活服务短板识别与优化建议.csv"),
        save_table(shortboard_count, "主要短板设施统计.csv"),
        save_table(
            candidate_distance_df.round({"距离_m": 2, "生活点需求权重": 2}),
            "候选点到生活点距离表.csv",
        ),
        save_table(candidate_scores_df, "新增服务设施候选点评分结果.csv"),
        save_table(best_candidate, "最优候选点.csv"),
    ]

    report_path, docs_report_path = create_report(
        final_accessibility_table,
        final_shortboard_result,
        shortboard_count,
        candidate_scores_df,
        best_candidate,
    )
    readme_path = create_readme(final_accessibility_table, shortboard_count, best_candidate)
    report_paths = [report_path, docs_report_path, readme_path]

    project_summary_df = create_project_summary(
        table_paths=table_paths,
        geojson_paths=geojson_paths,
        figure_paths=figure_paths,
        report_paths=report_paths,
    )
    project_summary_path = save_table(project_summary_df, "项目成果清单.csv")
    table_paths.insert(0, project_summary_path)

    best_row = best_candidate.iloc[0]
    highest_accessibility = final_accessibility_table.iloc[0]
    lowest_accessibility = final_accessibility_table.iloc[-1]

    print("项目运行完成：基于模拟数据的校园生活服务设施可达性与优化分析")
    print("重要声明：本项目使用模拟数据，结果仅用于方法训练和流程演示。")
    print(
        f"综合可达性最高生活点：{highest_accessibility['生活点名称']} "
        f"({highest_accessibility['综合可达性指数']:.3f})"
    )
    print(
        f"综合可达性最低生活点：{lowest_accessibility['生活点名称']} "
        f"({lowest_accessibility['综合可达性指数']:.3f})"
    )
    print(
        f"新增自助打印点最优候选点：{best_row['候选点名称']}，"
        f"综合选址得分 {best_row['综合选址得分']:.3f}，"
        f"加权平均服务距离 {best_row['加权平均服务距离_m']:.3f} 米"
    )
    print(f"CSV 输出路径：{TABLE_DIR.resolve()}")
    print(f"GeoJSON 输出路径：{GEOJSON_DIR.resolve()}")
    print(f"PNG 图片输出路径：{FIGURE_DIR.resolve()}")
    print(f"Markdown 报告输出路径：{REPORT_DIR.resolve()}")
    print(f"README 路径：{readme_path.resolve()}")


if __name__ == "__main__":
    main()
