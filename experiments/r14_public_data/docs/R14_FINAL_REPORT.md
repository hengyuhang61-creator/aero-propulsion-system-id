# R14 最终报告：公开航空实验数据的取得、资格审查与低阶建模

**执行日期：** 2026-10-31
**研究目录：** `C:\Work\research\aviation_algorithm_r14_public_data_20261031`
**GitHub 分支：** `r14-public-data-experiments`
**执行方式：** 本会话本体直接执行，无子代理、无委派

---

## 0. 一页结论

本轮**真实取得了** NASA SBLI2.05 UQ 全部 45 个扰动工况 + 基准（54.4 MB，241 文件）与 NASA HMVE 2025 的 23 个 PIV 剖面文件（483 条剖面），并完成了**留组交叉验证**的低阶建模与流场 POD 重构。

**核心定量结果：**
- 留一扰动位置（未见位置，9 折）：Δx_scp RMSE **0.65 mm**（信号跨度 5.12 mm 的 12.7%），Δy_scp RMSE **0.20 mm**
- 留一扰动高度（未见高度，5 折）：Δx_scp RMSE **0.44 mm**，Δy_scp RMSE **0.14 mm**
- 流场 POD + 系数回归：U RMSE **16.0 m/s**（相对最近邻基线改善 13.5%，相对均值场 21%）；**V 分量不如最近邻基线**
- 边界外推误差是域内的 **2–2.5 倍**

**未完成项（有明确阻断证据）：** Busemann 视频（CDN 限速实测 0.04–0.6 KB/s）、CFD 对照（三维构型 + 几何假设）、任何动态辨识（无同步瞬态数据）。

---

## 1. 分项交付状态

| 状态项 | 判定 | 依据 |
|---|---|---|
| `DATA_ACCESS` | **PASS** | 28 个文件 `VERIFIED_DOWNLOADED`，总计 205.8 MB，全部 SHA256 已登记（`SHA256SUMS.txt`） |
| `MODEL_RESULT` | **PASS** | 两种留组验证 × 4 个模型 × 2 个目标，指标含单位（`results/sbli205_cv_metrics.csv`） |
| `VIDEO_TRACKING` | **BLOCKED** | 视频未取得；管线已交付并用合成片验证代码路径；无实验轨迹 |
| `CFD_VALIDATION` | **NOT_EXECUTED** | 未运行求解器；四算例与几何规范已冻结（`07_CFD_COMPARISON.md`） |
| `DYNAMIC_IDENTIFICATION` | **NOT_ELIGIBLE** | 所有取得的数据均为系综平均，无独立激励 + 同步物理时间输出 |
| `SCIENTIFIC_VALIDATION` | **PARTIAL** | 单数据集内留组泛化已评估；跨实验（HMVE）仅建立比较契约，未验证模型 |
| `DELIVERY_STATUS` | **PARTIAL_DELIVERED** | 数据、代码、结果、报告、测试、GitHub 分支齐备；视频与 CFD 未交付 |

---

## 2. 实际取得了什么

| 文件 | 大小 [B] | SHA256（前 16 位） | 状态 |
|---|---:|---|---|
| `UQ_experiment.zip` | 54,397,190 | `fe163f694e6c0450` | VERIFIED_DOWNLOADED |
| `HMVE2_PIVprofiles.zip` | 950,326 | `a63d723ef1701b94` | VERIFIED_DOWNLOADED |
| `Campo_thesis.pdf` | 48,031,354 | `6e2ea02aa867fcb6` | VERIFIED_DOWNLOADED（246 页） |
| `README_UQ.pdf` | 105,569 | `9c002d751f0f12af` | VERIFIED_DOWNLOADED |
| `Reising_TM-20250008885.pdf` | 97,753,562 | `e1dba25065e4bdb9` | VERIFIED_DOWNLOADED（64 页；首次下载被截断，已整文件重下） |
| `data.Mach46.txt` | 5,789 | — | VERIFIED_DOWNLOADED（NPARC Study #1） |
| HMVE `.dat` × 23 | 4.58 MB 解压 | 逐文件登记 | VERIFIED_DOWNLOADED |
| Busemann 视频 × 7 | 0 | — | **BLOCKED** |

完整清单：`01_DATA_CATALOG.csv`、`manifest.json`、`SHA256SUMS.txt`。

---

## 3. 实际运行了什么

全部脚本位于 `src/`，均在本机执行并产出 `results/`、`figures/`：

| 脚本 | 作用 | 产出 |
|---|---|---|
| `sbli205_io.py` | 解析 45 工况 + 基准，网格与掩码核对 | `data/processed/sbli205_grid.npz`、`data/manifests/sbli205_dataset_meta.json` |
| `sbli205_model.py` | 4 模型 × 2 种留组验证 + h→0 一致性 | `sbli205_cv_metrics.csv` 等 4 个 CSV/JSON |
| `sbli205_pod.py` | 留位置 POD + GP 系数回归 + 秩扫描 4–20 | `sbli205_pod_metrics.csv`、`sbli205_pod_folds.json` |
| `hmve_analysis.py` | 23 文件 483 剖面解析与物理量提取 | `hmve_station_metrics.csv`、`hmve_file_summary.csv` |
| `build_manifest.py` | 全量 SHA256 与目录 | `01_DATA_CATALOG.csv`、`SHA256SUMS.txt`、`manifest.json` |
| `export_artifacts.py` | 案例表与 POD 示例场 | `sbli205_cases.csv`、`pod_example_fields.npz` |
| `make_figures.py` | 4 张主图 | `figures/fig01–fig04` |
| `busemann_video.py` | 视频元数据 + 双路线追踪 + 输出契约 | 工具（合成片验证） |
| `fetch_videos_hls.py` | 分片级视频下载 | 失败证据 |

测试：`tests/test_r14.py`（5 项，全 PASS）、`tests/test_video_code_path.py`（4 项，全 PASS）。

---

## 4. 可复现结果

### 4.1 激波穿越点回归

| 验证方案 | 目标 | 最佳模型 | MAE [mm] | RMSE [mm] |
|---|---|---|---:|---:|
| 留位置 | Δx_scp | 三次多项式 | 0.498 | 0.650 |
| 留位置 | Δy_scp | 二维插值 | 0.161 | 0.204 |
| 留高度 | Δx_scp | GP (Matérn-5/2) | 0.306 | 0.439 |
| 留高度 | Δy_scp | GP | 0.110 | 0.144 |

**关键发现：没有单一方法全面占优。** GP 在高度插值上比二次响应面 RMSE 低 49%，但在位置外推上最差（1.05 vs 三次 0.65），原因是 GP 远离数据时回归先验均值，表现为 −0.28 mm 的系统偏差。

### 4.2 流场 POD

| 模型 | U RMSE [m/s] | V RMSE [m/s] |
|---|---:|---:|
| POD+GP（秩 4–20） | 16.0–16.1 | 7.00–7.08 |
| 最近邻案例 | 18.5 | **6.84** |
| 训练均值场 | 20.3 | 9.42 |

秩 4→20 几乎无变化（93.4% → 99.5% 能量），说明**瓶颈是只有两个输入变量的系数映射，不是模态基**。

### 4.3 物理解释

- 高度敏感度 dΔx/dh 从 −0.33（x=−75.2）变化到 **−6.76**（x=−57.2），**20 倍差异，强交互**，且非单调
- Δy_scp 最大位移出现在 case 40（x=−48.2），与 Δx_scp 最大位移（case 25, x=−57.2）**不在同一位置**
- 结论：不能用单一"扰动强度"标量同时解释流向与法向位移

### 4.4 关键数据审查发现（本轮新增证据）

1. **ASCII `dataSummary` 表头列序与数值不符**（h 与 x 互换）。按字面解析会使全部建模失效。
2. **跨案例 X 网格按位置组平移，最大 2.04 mm**，与物理信号同量级。README 的坐标定义与实际文件不一致。
3. **`data.Mach46.txt` 不是 Mach 4.6**，而是 M≈0.46 的 Sajben 跨声速扩压器（NPARC Study #1，Hsieh et al. 1987）。
4. 论文 §4.6 推荐的最小 CFD 算例集是**基准 / case 25 / case 23 / case 4**，不是任务书初拟的 case 25/40/1。

---

## 5. 用户现在可以直接使用什么

| 用途 | 文件 |
|---|---|
| 全部原始数据（只读） | `data/raw/sbli205/UQ_experiment/`、`data/raw/hmve/HMVE2_PIVprofiles/`、`data/raw/nasa_study1/` |
| 45 工况设计表 | `results/sbli205_cases.csv` |
| 逐案例逐模型预测值 | `results/sbli205_cv_predictions.csv` |
| 汇总指标 | `results/sbli205_cv_metrics.csv`、`sbli205_pod_metrics.csv` |
| 可复用脚本 | `src/*.py`（依赖：`numpy scipy matplotlib scikit-learn pypdf pymupdf opencv-python-headless pandas`） |
| 论文原文 | `papers/Campo_thesis.pdf`、`papers/Reising_TM-20250008885.pdf` |
| 图表 | `figures/fig01–fig04` |

---

## 6. 仍然没有解决的问题

1. **没有动态数据。** 所有取得的数据都是系综平均；SBLI2.05 明确只有 2500 对图像的平均值。动态辨识在现有公开资源下不可行。
2. **视频未取得。** Busemann 2026/2025 的 7 份视频被 CDN 限速阻断；已记录吞吐量证据与完整恢复步骤。
3. **CFD 未运行。** 三维低展弦比构型 + bump 跨展向曲面需自建假设，本轮不制造"看起来成功的验证"。
4. **跨实验泛化未验证。** HMVE 只建立了比较契约，未能检验 SBLI2.05 模型。
5. **GP 不确定度未校准。** 未做覆盖率检验，不能当置信区间用。
6. **POD 的 V 分量不如最近邻。** 说明当前输入维度（2 个参数）不足以约束法向速度场。
7. **跨组坐标登记问题未解决。** 我们给出了判定依据，但没有外部基准能恢复真实绝对坐标。

---

## 7. 下一项最值得投入的科研行动

**排序（只做第一项）：**

1. **取得 Busemann 2026 视频并完成轨迹提取。** 这是本轮唯一"数据存在、路径已知、只差网络"的高价值缺口。恢复步骤已冻结在 `04_BUSEMANN_VIDEO_TRACKING.md` §5。完成后可交付位置—帧序号轨迹与不确定度，并可与论文公布轨迹做一致性审计（不是独立验证）。
2. 其次：对 SBLI2.05 四算例做三维 RANS（规范已冻结，`07_CFD_COMPARISON.md` §4）。
3. 再次：GP 不确定度的校准检验（覆盖率/可靠性图）。

---

## 8. 十问回答

1. **是否取得真实、可追溯的航空实验数据？** 是。SBLI2.05 UQ（45+1）与 HMVE（483 剖面），全部 SHA256 可核。
2. **能否预测未参与训练的完整实验工况？** 能，但有界。留位置 Δx RMSE 0.65 mm；边界外推误差翻 2–2.5 倍。
3. **能否重建有物理意义的平均流场？** 能重建平均 U/V 场（U RMSE 16 m/s ≈ 3.3% U∞），但未达测量不确定度，V 分量不如查表基线。
4. **是否优于原始研究或简单基线？** 与原文无法比较（原文未发表响应面）。与自建基线比较：高度方向优于多项式 49%，位置方向不如三次多项式，V 分量不如最近邻。**没有全面优势。**
5. **是否有独立实验数据支持物理解释？** 部分。HMVE 支持"亏损随激波强度加深"，但无法检验"位置非单调敏感度"（无对应自由度）。
6. **是否真正建立了动态输入输出模型？** 否。无同步瞬态数据。
7. **哪些结果有发表价值？** 留组泛化边界 + 坐标登记不一致的发现 + "GP 在插值区强、外推区弱"的定量证据。这些是方法学贡献，不是物理新发现。
8. **哪些只是工程复现或数据处理？** 45 工况索引、POD 重构、HMVE 剖面提取、SHA256 台账，均为工程复现。
9. **最大科学证据缺口？** 缺少"独立激励 + 同步物理时间输出"的公开数据。这是整个方向的瓶颈，不是本轮的实现问题。
10. **下一项最值得投入的实际行动？** 取 Busemann 视频做轨迹提取（见 §7）。

---

## 9. 诚实声明

本轮**没有**发现新的非启动物理规律，**没有**建立动态模型，**没有**完成 CFD 验证，**没有**证明跨实验泛化。已交付的是：真实数据、可复现代码、留组验证的定量泛化边界、以及对公开数据包内部不一致的三项独立审计发现。
