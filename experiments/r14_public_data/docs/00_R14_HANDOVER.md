# R14 交接说明

**目录：** `C:\Work\research\aviation_algorithm_r14_public_data_20261031`
**生成时间：** 2026-10-31
**状态：** `PARTIAL_DELIVERED`（数据与建模完成；视频与 CFD 未完成，均有阻断证据）

---

## 1. 三十秒上手

```bash
cd C:\Work\research\aviation_algorithm_r14_public_data_20261031
PY=C:\Users\14864\.workbuddy-ai\binaries\python\envs\r14\Scripts\python.exe

$PY src/sbli205_io.py        # 重建 processed 数组 + 网格核对
$PY src/sbli205_model.py     # 4 模型 × 留位置/留高度
$PY src/sbli205_pod.py       # POD + GP 系数回归（约 3–5 分钟）
$PY src/hmve_analysis.py     # 483 条剖面
$PY src/export_artifacts.py  # 案例表 + POD 示例
$PY src/make_figures.py      # 4 张图
$PY tests/test_r14.py        # 5 项断言
$PY tests/test_video_code_path.py   # 4 项断言（合成片）
```

Python 环境：`C:\Users\14864\.workbuddy-ai\binaries\python\envs\r14`
依赖：numpy scipy matplotlib scikit-learn pypdf pymupdf opencv-python-headless pandas

---

## 2. 文档地图

| 想知道 | 读 |
|---|---|
| 总体结论与十问 | `R14_FINAL_REPORT.md` |
| 数据能不能用、有哪些坑 | `02_DATA_ELIGIBILITY_AUDIT.md` |
| 事前定的规则 | `03_RESEARCH_PROTOCOL.md` |
| 建模结果与创新性判断 | `05_SBLI205_ROM_REPORT.md` |
| HMVE 交叉验证到哪一步 | `06_HMVE_CROSS_VALIDATION.md` |
| 视频为什么没做 | `04_BUSEMANN_VIDEO_TRACKING.md` |
| CFD 为什么没跑、下次怎么跑 | `07_CFD_COMPARISON.md` |
| 不能说什么 | `08_LIMITATIONS.md` |

---

## 3. 三个必须先知道的坑

1. **ASCII `dataSummary` 表头列序是错的**（写成 x_bump, h_bump，实际是 h_bump, x_bump）。任何重新解析都必须按 `dataMatlab_caseN.mat` 或 README Table 1 的语义。
2. **跨案例 X 网格不一致**，按位置组整体平移，最大 2.04 mm。做任何跨案例场比较前必须显式声明对齐方式。
3. **`data.Mach46.txt` 是 M≈0.46 的跨声速扩压器**，不是 Mach 4.6。

---

## 4. 未完成项与恢复路径

| 项 | 恢复动作 |
|---|---|
| Busemann 视频 | `src/fetch_videos_hls.py`（分片下载，避免 ffmpeg 挂起），在带宽更好的环境执行；随后 `src/busemann_video.py` 的 probe → 人工标注 → 自动追踪 |
| CFD | 按 `07_CFD_COMPARISON.md` §4 冻结规范执行；四算例 = 基准 / case 25 / case 23 / case 4 |
| GP 不确定度校准 | 在现有 CV 预测上做覆盖率统计，无需新数据 |

---

## 5. 与历史轮次的关系

- **R11**（`aero-propulsion-system-id`）：其"BLOCKED_WITH_EVIDENCE"结论未被推翻。本轮没有把 Sajben 两组数据包装成训练库；`data.Mach46.txt` 的核实反而**加强了** R11 的判断（该文件是同几何族的另一个稳态工况，不构成 31 工况数据库）。
- **R13**：CFDVAL2004 谐波计算未重跑。`data.Mach46.txt` 是 R13 报告列出的 next 项，本轮已取得并完成性质核实。
- **R01–R13 正式资产**：未删除、未移动、未覆盖。
