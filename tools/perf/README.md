# Performance Tools (macOS/Linux)

## 1) Process Monitor (per component)

```bash
python tools/perf/monitor_processes.py \
  --target sim=mac-main_hako_drone_service \
  --target vis=python\\ -m\\ http.server\\ 8001 \
  --drone-count 10 \
  --label fleets_scale \
  --duration-sec 60 \
  --interval-sec 1 \
  --output logs/perf/raw_n10.csv
```

`--target` は `name=PID` または `name=pgrep_pattern` を指定します。

## 2) Host Monitor (whole machine)

```bash
bash tools/start-host-perf-monitor.bash 1 fleets_scale_n1 3600
```

出力は固定ファイル名（日時なし）で上書きされます:
- `logs/perf/raw_fleets_scale_n1.csv`
- `logs/perf/raw_host_fleets_scale_n1.csv`

直接実行する場合:

```bash
python tools/perf/monitor_host.py \
  --drone-count 1 \
  --label fleets_scale_n1 \
  --duration-sec 3600 \
  --interval-sec 1 \
  --output logs/perf/raw_host_fleets_scale_n1.csv
```

## 3) Aggregate

```bash
python tools/perf/aggregate_metrics.py \
  --input logs/perf \
  --output logs/perf/summary.csv
```

`target_name=host` がホスト全体の結果です。

## 4) Estimate Capacity

```bash
python tools/perf/estimate_capacity.py \
  --input logs/perf/summary.csv \
  --metric cpu_p95 \
  --limit 85 \
  --output logs/perf/capacity.csv
```

`capacity.csv` の `estimated_max_drones` を 1台構成の概算耐容量として利用します。

## 5) Plot Graphs

```bash
python tools/perf/plot_summary.py \
  --input logs/perf/summary.csv \
  --output-dir logs/perf
```

出力:
- `logs/perf/cpu_avg_vs_drone_count.png`
- `logs/perf/cpu_p95_vs_drone_count.png`
- `logs/perf/rss_avg_vs_drone_count.png`
