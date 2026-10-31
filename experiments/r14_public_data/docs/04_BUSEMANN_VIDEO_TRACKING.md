# R14 Busemann 非启动视频轨迹提取

**状态：`VIDEO_ONLY` → `BLOCKED`（未取得视频）；轨迹提取未执行。**
**交付物：可运行的视频处理管线（已用合成片验证代码路径），不交付任何实验轨迹。**

---

## 1. 视频取得尝试的真实记录

### 1.1 目标

| 论文 | DOI | 补充材料 |
|---|---|---|
| Schram & Narayanaswamy 2026, *Unstart dynamics of hypersonic Busemann inlet at non-zero angles of attack* | `10.1007/s00348-026-04215-0` | 5 份 mp4（文章内标注 8139 / 32534 / 9067 / 25360 / 4406 KB） |
| Johnson & Narayanaswamy 2026（2025 年 12 月卷）, Busemann restart | `10.1007/s00348-025-04156-0` | 2 份补充视频 |

### 1.2 取得路径与实测结果

1. 文章页面 HTTP 200 可取（434,918 B / 440,577 B），确认 5 份与 2 份视频的存在与大小。
2. 页面内嵌 `<iframe data-src="//e.video-cdn.net/watch?video-id=...">`，视频由 Movingimage CDN 托管，**不提供传统 `static-content.springer.com/esm/...MOESM1_ESM.mp4` 直链**（探测 MOESM1–5 × mp4/avi 全部返回 403）。
3. 播放页可解析出带时效令牌的主播放列表；4 个码率变体：512×288 / 640×360 / 854×480 / **1280×720 (2.1 Mbit/s)**。
4. 最高码率变体共 **6 个分片**，单片 0.92–1.13 MB。
5. **实测吞吐：** 30 秒仅取得 1.2 KB / 17.8 KB（约 0.04–0.6 KB/s），curl 全部 `Operation timed out`。
6. `ffmpeg -i <master.m3u8>` 直接挂起 >300 s 无输出（两次尝试）。

**失败证据已保存：** `logs/video_fetch_2026.log`、`logs/video_download_busemann2026.json`、`logs/mi_player.html`、`logs/springer_10.1007_s00348-026-04215-0.html`。

**结论：在本机网络条件下无法在合理时间内取得视频。不虚构视频，不虚构轨迹，不虚构速度。**

---

## 2. 为什么即使取得视频也不能给物理速度（预先声明的约束）

以下限制在取得视频之前就已写入设计，不因取得失败而改变：

| 限制 | 后果 |
|---|---|
| 论文报告 PSP −6 dB 衰减频率约 10 kHz，且**未做增益滚降修正** | 20 kHz 图像采样率 ≠ 20 kHz 有效压力带宽 |
| 论文报告瞬时压力总体误差约 10%，激波速度不确定度 ±14 m/s | 任何自算速度必须与 ±14 m/s 比较才有意义 |
| 原始数值数据需联系通讯作者 | 视频不是压力场数据库 |
| CDN 交付版本最高 1280×720 且经过转码 | 论文的 4.5 px/mm（schlieren）、1.4 / 2 binned px/mm（PSP）标定**不能直接继承**，必须重新标定 |
| 视频无实验时钟信息 | 只能给 `frame_index`，不能给 `time_s` |

因此管线在默认状态下**只输出位置—帧序号**，只有在 `time_base_verified=True` 且提供 `px_per_mm` 时才写速度列。

---

## 3. 已交付的管线（`src/busemann_video.py`）

### 3.1 元数据（`probe`）

用 `ffprobe -count_frames` 取：编码、分辨率、`r_frame_rate`、`avg_frame_rate`、实际帧数、时长、容器；
`is_vfr_suspect` 通过比较 `r_frame_rate` 与 `avg_frame_rate` 判定可变帧率嫌疑（差 >1e-3）。
**不使用播放器显示时间。**

### 3.2 两条识别路线

| 路线 | 原理 | 输出 | 禁止 |
|---|---|---|---|
| `track_schlieren` | 沿扫描带取流向灰度剖面，找 `\|dI/dx\| > mean + k·σ` 的首个位置 | 像素位置 + 置信度 | 不得把灰度梯度换算为绝对压力 |
| `track_psp_threshold` | 归一化强度比 `R = I/I_ref` 的阈值穿越（论文用 R=0.35） | 像素位置 + 置信度 | 无标定/参考帧时不得称为压力 |
| `interpolate_manual` | 人工标注少量关键帧后线性插值，作为可审计参考 | 逐帧位置 | 需人工输入，不可自动替代 |

### 3.3 输出契约（`write_trajectory`）

- 时间基准可靠 + 有空间标定 → `frame_index, time_s, shock_x_mm, shock_v_m_s, uncertainty_mm, tracking_confidence`
- 否则 → `frame_index, shock_x_pixel, tracking_confidence`

该行为由测试强制（`tests/test_video_code_path.py::t_output_contract`）。

---

## 4. 代码路径验证（合成片，**非实验证据**）

`tests/test_video_code_path.py` 生成 40 帧、320×180、已知匀速平移 2 px/帧的合成阶跃片：

| 检查 | 结果 |
|---|---|
| ffprobe 元数据（40 帧、320×180、CFR） | PASS |
| 追踪器相对已知真值的误差（最大 ≤3 px，平均 ≤1.5 px） | PASS |
| 人工锚点插值端点与中点正确 | PASS |
| 输出契约：无时间基准 → 仅像素；有时间基准+标定 → 含速度 | PASS |

**这只能证明代码可用，不能证明任何 Busemann 物理结论。**

---

## 5. 恢复条件（下一轮可直接执行）

1. 在网络条件更好的环境重新执行 `src/fetch_videos_hls.py`（已实现分片下载+拼接，避免 ffmpeg 挂起）。
2. 取得视频后先跑 `probe`，确认实际帧率、总帧数与是否 VFR。
3. 用论文图或视频中已知尺寸特征（如进气道唇口 44 mm 直径）重新建立 px/mm 标定，**不继承论文数值**。
4. 先做人工标注 20–30 帧作为审计参考，再跑自动阈值法，报告漏检率/误检率/轨迹差异。
5. 只有在能证明帧间时间间隔恒定的前提下，才允许输出 `time_s` 与速度；否则永久停留在 `frame_index`。
