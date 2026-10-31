# R14 数据资格审查报告

**执行日期：** 2026-10-31
**范围：** 本轮实际取得、实际读取、实际核验的公开航空实验数据
**原则：** 只有真实落盘并通过完整性/结构核对的文件才记为 `VERIFIED_DOWNLOADED`；网页上存在下载按钮不等于取得数据。

---

## 0. 总结判定

| 数据集 | 状态 | 独立工况数 | 可用于 | 不可用于 |
|---|---|---|---|---|
| NASA SBLI2.05 UQ（Campo/Eaton） | `VERIFIED_DOWNLOADED` | 45 + 1 基准 | 参数化激波位置回归、平均流场 POD 低阶重构 | 动态辨识、瞬态、湍流统计 |
| NASA HMVE 2025 PIV profiles | `VERIFIED_DOWNLOADED` | 23 个文件 / 483 条剖面 | 跨马赫数平均/湍流剖面比较 | 分离泡几何定量、壁压、绝对速度 |
| Campo 博士论文 / README_UQ | `VERIFIED_DOWNLOADED` | — | 方法、几何、变量定义 | — |
| NASA/TM-20250008885 | `VERIFIED_DOWNLOADED` | — | HMVE 条件、坐标定义 | — |
| NASA Study #1 `data.Mach46.txt` | `VERIFIED_DOWNLOADED` | 1 个稳态工况 | 跨声速扩压器稳态剖面参考 | 任何超声速/高马赫用途（**M≈0.46**） |
| Busemann 2026 五份 MP4 | `BLOCKED` | 0 | — | 轨迹提取 |
| Busemann 2025 两份 AVI | `BLOCKED` | 0 | — | 轨迹提取 |
| HyMAX / Speed Bump / G550 | `NOT_ATTEMPTED`（P2，本轮未进入） | 0 | — | — |

---

## 1. NASA SBLI2.05 UQ —— 主建模数据集

### 1.1 取得证据

- 官方页面：`https://tmbwg.github.io/turbmodels/Other_exp_Data/sbliM2.05_exp.html`（HTTP 200）
- 实际下载：`UQ_experiment.zip`，54,397,190 B，SHA256 `fe163f694e6c04508602c5cff294c802fece111ed1856b90bab9418e73a08ce4`
- ZIP 完整性：`testzip()` 返回 None；241 个条目；解压后 146,815,589 B
- 内部结构：`ASCII/` 47 文件（45 案例 + unperturbed + dataSummary）、`Matlab/` 48 文件、`Tecplot/` 136 文件、`InletProfileData/` 3 文件

### 1.2 变量与坐标（逐字核对 README_UQ.pdf）

| 变量 | 定义 | 单位 |
|---|---|---|
| X | `X = x_absolute − x_scp,unperturbed`，`x_absolute` 原点在压缩坡道脚 | mm |
| Y | 竖直坐标，原点在风洞下壁面 | mm |
| Z | 展向坐标，**所有案例 Z = 21 mm** | mm |
| U | 平均流向速度 | m/s |
| V | 平均竖直速度 | m/s |
| valid | 1 = 有效 PIV 矢量，0 = 有效矢量率过低 | — |

基准：`x_scp = 44.1 mm`，`y_scp = 4.84 mm`（README 与 `dataSummary.mat` 中 `y_scp_unperturbed = 4.84080815` 一致）。

### 1.3 网格与有效掩码（实测）

- 网格：125 × 153 = 19,125 点，MATLAB 与 ASCII 完全一致（抽样 case 1/2/45：max|ΔU| = 5.0e-7 m/s，valid 掩码 0 处不一致）
- ASCII 行数核对：`awk` 统计 19,125 行有效数据行，与 125×153 吻合
- 逐案有效点比例：见 `data/manifests/sbli205_dataset_meta.json` 的 `per_case_valid_fraction`
- **46 个场共同有效区：13,056 点（68.3%）**

### 1.4 发现 A：ASCII `dataSummary` 表头列序错误

文件头写作 `case number  x_bump  h_bump  Delta_x_scp  Delta_y_scp`，但数值列实际为 `(h_bump, x_bump, Δx, Δy)`。证据链：

1. README_UQ.pdf 第 4–5 页 Table 1 列序为 `case, h_bump, x_bump, Δx_scp, Δy_scp`；
2. `dataASCII_case1` 首行自述 `x_bump = -75.2 mm, h_bump = 0.11 mm`，与 `0.11, -75.20` 对应；
3. `dataMatlab_case1.mat` 中 `h_bump = 0.11`、`x_bump = -75.2`。

**处理：** 按数值语义解析，原始表头文本保留在解析器 docstring 与 manifest 中。若按表头字面解析，h 与 x 会互换，全部建模失效。

### 1.5 发现 B：跨案例网格并非同一坐标系

README 声明 X 以未扰动 scp 为基准，因此所有案例的 X 网格应当一致。实测不是：

| x_bump 组 | 相对 unperturbed 的 X 平移 [mm] | Y 平移 [mm] | 组内残差 [mm] |
|---|---:|---:|---:|
| −75.2 | −0.673 | 0.105 | ≤0.005 |
| −69.2 | 0.000 | 0.000 | 0 |
| −63.2 | −0.443 | 0.008 | ≤0.005 |
| −60.2 | −0.526 | 0.154 | ≤0.011 |
| −57.2 | −0.443 | 0.023 | ≤0.005 |
| −54.2 | −0.526 | 0.147 | ≤0.005 |
| −51.2 | +1.283 | 0.124 | ≤0.011 |
| −48.2 | +2.035 | 0.034 | ≤0.011 |
| −42.2 | +1.169 | 0.072 | ≤0.011 |

即：平移在组内是**严格常数**（残差 ≤0.011 mm），在组间最大达 **2.04 mm**，与物理信号 Δx_scp 的量级（−4.76…+0.42 mm）相当。

**这是公开数据包内部的坐标登记不一致，不是我们的处理误差。**

### 1.6 发现 C：对齐方式的定量判定（不是靠假设）

对 45 个案例分别计算与未扰动场的 RMS 速度差，比较两种对齐：

| 对齐方式 | 与 \|Δx_scp\| 的相关系数 | 中位 RMS |
|---|---:|---:|
| 按网格索引对齐（忽略坐标平移） | **0.926** | 21.7 m/s |
| 按原始坐标插值对齐 | 0.734 | 19.1 m/s |

索引对齐与物理扰动幅度的一致性显著更高，故 POD 采用索引对齐，并在报告中把它作为**显式选择**而非默认事实记录。小扰动案例（\|Δx_scp\|<0.1 mm）的 RMS 差为 3.3–14.0 m/s，构成**约 10 m/s 的测量噪声底**（≈2% U∞）。

### 1.7 发现 D：论文正文与数据包的位置编号不一致

论文 §4.4（PDF 第 133 页）写作 `xbump = −72.2, −69.2, …, −42.2 mm`；数据包与 README Table 1 为 `−75.2, …, −42.2 mm`。建模以**数据包**为准，差异记录在案。

### 1.8 可支持 / 不可支持的结论

- 可支持：45 工况的 Δx_scp/Δy_scp 参数映射、留位置/留高度泛化评估、平均 U/V 场低阶重构
- 不可支持：任何动态/瞬态结论（只有 2500 对图像的平均量，无时间序列）；湍流统计（数据包不含雷诺应力）；绝对压力（无壁压）
- 使用限制：1.1 mm 坡道专属，禁止与 3 mm / 5 mm 坡道数据混合

---

## 2. NASA HMVE 2025 —— 独立交叉验证集

### 2.1 取得证据

- NTRS 记录 `20250008885`，标题：*Turbulent Shock-Wave/Boundary-Layer Interactions Without Sidewall Effects at Mach 2.5, 3.0, and 3.5 — PIV Measurements From 2025 Test Entry*
- `HMVE2_PIVprofiles.zip`：950,326 B，SHA256 `a63d723ef1701b94eec0dad3c1a984b43e8ea894b4e844116138c318ebb7655e`，`testzip()` 通过
- `Reising_TM-20250008885_Final.pdf`：97,753,562 B，64 页（首次下载被截断为 87,326,720 B 且 PDF 页树损坏；服务器不支持 Range，必须整文件重下——已重下并验证 64 页可解析）
- 23 个 `.dat`（18 轴对称 + 5 swept），483 条剖面，21 站/文件

### 2.2 实际字段（Tecplot ASCII 头）

`(x − x_i), y, U/U1, V/U1, W/U1, uu/U1², vv/U1², ww/U1², uv/U1²`

- `x_i` = 无粘激波入射位置（TM 报告 §III.A：以峰值负散度定位，用于修正激波发生器位置偏差）
- 归一化基准为**自由来流速度 U1**，不是当地边界层外缘速度
- **不含绝对速度（m/s）、不含壁压、不含壁面摩擦**

### 2.3 条件矩阵（实测文件名）

- Mach 2.5：α = 10°/13.5°/16°，Re-code 1/2/4
- Mach 3.0：α = 10°/13.5°（Re 2.25）、α = 16°（Re 1/2.25）
- Mach 3.5：α = 10°/13.5°（Re 3）、α = 16°（Re 1.5/3）
- swept：α = 16°，θ = 90°，Mach 2.5/3.0/3.5

重复工况（同一 Mach/α 不同 Re-code）**是不同雷诺数条件，不是重复实验**，不能当作独立重复样本。

### 2.4 关键限制（实测）

- 剖面第一个测点在 y ≈ 0.70 mm，近壁 0–0.7 mm 缺失 → δ*、θ 系统性偏低；已给出线性近壁补正（`delta_star_trunc_corr_mm`）
- 全部 483 条剖面中 `U/U1` 最小值 ≥ 0.0008，**没有任何负速度**：报告所述"16° 完全分离"的反向流区未被这些剖面解析。因此本数据**不能**用于分离泡长度/高度的定量测量，只能给出速度亏损与湍流增强的定量比较
- y 原点由逐数据集目视确定（TM 报告 §III），存在亚毫米级不确定度

---

## 3. `data.Mach46.txt` —— 本轮线索核实（重要纠正）

### 3.1 文件事实

| 项目 | 核实结果 |
|---|---|
| 真实路径 | 官方 `https://www.grc.nasa.gov/www/wind/valid/transdif/transdif01/data.Mach46.txt`（HTTP 200，5,789 B，207 行）；本地副本 `data/raw/nasa_study1/data.Mach46.txt` |
| 本地先前是否存在 | **不存在**。全盘 `find /c/Work /c/Users/14864 -iname "*mach46*"` 无结果；R13 报告把它列为"next"，但从未取得 |
| 来源 | NPARC Alliance Validation Archive，*Sajben Transonic Diffuser: Study #1* |
| 原始文献 | Hsieh, Wardlaw, Bogar, Coakley (1987), "Numerical Investigation of Unsteady Inlet Flowfields," AIAA J. 25(1):75–81；页面另列 Chen/Sajben/Kroutil (1979)、Bogar/Sajben/Kroutil (1983)、Salmon et al. (1983)、Sajben et al. (1984)、Bogar (1986) |
| 数据性质 | **实验数据**（作者提供的表格化数据），非 CFD 输出 |
| **Mach 数** | **进口 M ≈ 0.46**，喉道下游加速至略低于 1.3，激波降至约 0.78，出口约 0.51。文件名 "Mach46" = **Mach 0.46**，不是 Mach 4.6 |
| 几何 | Sajben 收缩-扩张扩压器，喉道高 `h_thr = 0.14435 ft = 4.407 cm`；与 R11 已用的 Sajben 几何（H = 0.04399788 m）同族 |
| 单位/坐标 | 长度以喉道高 H 归一化（X/H、Y/H）；压力为 P/P0；速度 m/s |
| 内容 | 上/下壁面静压（各 32–33 点）+ 4 个站位的轴向速度剖面（X/H = 1.729、2.882、约 4.6、6.340） |
| 配套 | 同目录提供 `transdif01.tar`（含 `sajben.cgd` 网格、Plot3D 文件），本轮未下载 |
| 为何未进入 R11 资格 | R11 的检索范围是"31 工况跨工况数据库"与 Busemann 动态数据，未检索 NPARC 归档目录；该文件在 R13 才被列为后续项，但未实际取得 |

### 3.2 判定

- **不能**用于任何超声速/高超声速用途。把它当作"Mach 4.6 超声速进气道数据"是文件名的误读。
- **可以**用于：跨声速扩压器稳态速度剖面/壁压的独立参考；与 R11 的 Sajben 弱/强激波工况做同几何族的稳态对照（但工况点不同，不能合并训练）。
- **在 R14 中的定位：仅作参考，不进入 SBLI2.05 建模**。它与 SBLI2.05 的几何、马赫数、测量定义全部不同。

---

## 4. Busemann 视频：`BLOCKED`（含实测证据）

- 2026 论文（DOI `10.1007/s00348-026-04215-0`）确认为 **5 份 mp4** 补充材料，文章内标注大小 8139 / 32534 / 9067 / 25360 / 4406 KB
- 2025 论文（DOI `10.1007/s00348-025-04156-0`）确认为 **2 份**补充视频
- 两者均通过 `e.video-cdn.net`（Movingimage）播放器提供，HLS 分片 + 时效令牌
- 实测：主播放列表 200 可读；最高码率变体 `b2100000`（1280×720，2.1 Mbit/s）共 6 个分片，单片约 0.92–1.13 MB；**30 秒仅取得 1.2–17.8 KB**（约 0.6–18 KB/s），单片下载超时
- ffmpeg 直连 m3u8 挂起 >300 s 无输出

**结论：** 在本机网络条件下无法在合理时间内取得视频。已记录 URL、分片清单与吞吐量实测值。**不虚构视频，不虚构轨迹。** 视频处理管线已作为可运行工具交付并用合成片验证（见 `04_BUSEMANN_VIDEO_TRACKING.md`）。

---

## 5. 未进入本轮的数据（P2/P3）

HyMAX、Boeing Speed Bump/SBSE（约 3.1 GB，含 2.7 GB 瞬时壁压）、NASA 高超声速 SBLI 库、G550 飞行壁压：本轮未下载。原因是 P0 数据已构成完整可交付链，且这些数据需要单独的资格审计（时间戳/通道定义/许可）。状态记为 `NOT_ATTEMPTED`，**不记为已取得或已排除**。

---

## 6. 许可与再分发

- SBLI2.05 页面未声明明确再分发许可；论文由作者授权在 TMBWG 页面分发。本轮**不镜像原始数据到 GitHub**。
- HMVE 为 NASA 公开 NTRS 记录。
- 视频为 Springer 补充材料，未取得（无再分发问题）。
- 所有原始文件仅本机只读保留，GitHub 只提交脚本、清单、结果摘要与报告。
