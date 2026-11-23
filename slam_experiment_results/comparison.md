# SLAM map comparison

Reviewed the exported maps for Experiments A through K. The side-by-side
comparison is in [comparison_all.png](./comparison_all.png). Occupied-cell
percentages describe each saved image; they are not standalone map-quality
scores. The focused loop-closure comparison is in
[loop_closure_comparison.png](./loop_closure_comparison.png).

| Experiment | Settings changed from baseline | Map size | Origin (m) | Occupied cells |
|---|---|---:|---|---:|
| A | 10 Hz; no LiDAR or odometry noise | 238 x 238 | (-1.96, -4.45) | 3,177 / 56,644 (5.6%) |
| B | LiDAR 5 Hz | 238 x 238 | (-1.95, -4.44) | 3,048 / 56,644 (5.4%) |
| C | LiDAR 5 Hz; LiDAR noise 0.01 m | 243 x 240 | (-1.99, -4.55) | 5,767 / 58,320 (9.9%) |
| D | Odometry wheel radius 0.047 m vs physical 0.05 m | 239 x 239 | (-1.95, -4.45) | 3,673 / 57,121 (6.4%) |
| E | Wheel friction coefficient 0.4 | 250 x 244 | (-2.07, -4.76) | 5,447 / 61,000 (8.9%) |
| F | Drive wheel separation 0.28 m vs physical 0.34 m | 252 x 252 | (-2.02, -5.03) | 5,794 / 63,504 (9.1%) |
| G | Odometry noise 0.001 m and 0.001 rad per moving update | 239 x 238 | (-1.98, -4.43) | 3,572 / 56,882 (6.3%) |
| H | Odometry noise 0.003 m and 0.003 rad per moving update | 240 x 239 | (-1.96, -4.48) | 3,488 / 57,360 (6.1%) |
| I | Same noise as H; seed 7 | 240 x 240 | (-1.98, -4.50) | 3,549 / 57,600 (6.2%) |
| J | Baseline sensor and odometry settings; loop-closure route | 274 x 259 | (-2.14, -5.63) | 5,970 / 70,966 (8.4%) |
| K | Repeated baseline loop-closure run | 238 x 238 | (-1.94, -4.46) | 3,191 / 56,644 (5.6%) |

## Visual observations

- **A vs B:** The room and obstacle outlines appear very similar. Reducing the
  LiDAR rate did not show a clear improvement in wall alignment or consistency
  in this run.
- **C:** The map has visibly more speckling and irregular or discontinuous
  marks around walls and obstacles than A and B. Added LiDAR noise coincided
  with a less clean map.
- **D:** The map remains visually close to A despite the wheel-radius mismatch.
  The mismatch did not produce an obvious large distortion in this saved map.
- **E and F:** Both show substantially more distortion than A. E has noisy,
  smeared wall marks; F has displaced or broken wall segments and obstacle
  marks. These runs are consistent with slip and wheel-separation error
  affecting odometry, respectively.
- **G:** The map looks broadly similar to A and D. The small tested odometry
  noise level did not create an obvious large map distortion.
- **H:** The map also looks clean and broadly similar to A and G. Increasing
  the tested odometry noise to 0.003 per moving update did not create an
  obvious large map distortion in this run.
- **H vs I:** The maps look very similar despite using different random seeds.
  The tested noise level did not cause an obvious large change across these
  two runs.
- **J:** The final map is substantially more distorted than the clean
  baseline, with displaced/bent wall segments and large unexplored regions.
- **K:** The repeated loop-closure map looks clean and very similar to A. You
  reported no issue when revisiting the same place. This suggests the J
  distortion was not a consistent result of loop closure; route coverage or
  driving differences may explain why J looks different.

## Interpretation and caveats

Across these saved maps, the LiDAR-rate reduction (B) did not clearly improve
the result, and the tested odometry-noise level (G) appears mild. C, E, and F
look less consistent than A, but the differences may also reflect route
coverage, run duration, speed, or turning differences. The clean K result
supports that loop closure can run without visible mapping problems, though a
final map alone cannot prove a loop was detected or quantify its correction.
H and I provide a small check across noise seeds; repeat controlled runs for
stronger conclusions.
