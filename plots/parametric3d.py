import numpy as np
import math
import matplotlib.pyplot as plt
from transforms_function import *

task_impedance_ts = np.load("data/ts_data_taskimp.npy")[700:, :]

# font dictionary to standardize
font = {
    "family": "serif",
    "math_fontfamily": "cm",
    "color": "black",
    "weight": "semibold",
    "size": 13,
}

Amp = 9.80665 * 5 / 1000 # [m]
wu  = 3.00  # [Hz]
dt  = 0.01
steps = math.ceil(2 * math.pi / (dt * wu))

simulation_params = {"Kd": 1000, "Dd": 8, "Md": 0.016, "wu": wu}
parameters_set = [
    {"Kd": 1000, "Dd": 0.0, "Md": 0, "wu": wu},
    {"Kd": 1000, "Dd": 300, "Md": 0, "wu": wu},
]

# 1st dim: time, 2nd dim: parameters_set, 3rd dim: {x,y,z}
curves = np.zeros(
    (steps, len(parameters_set), 3)
)

# Generate Curves:
for j, param in enumerate(parameters_set):
    for k in range(steps):
        Tx, Ty, Tz = transforms(param)
        curves[k, j, :] = (
            Amp * Tx
            @ Ty
            @ Tz
            @ np.array([math.cos(wu * k * dt), math.sin(wu * k * dt), 0]).T
        )

# 3D plot with projections:
ax = plt.figure().add_subplot(
    projection="3d", xticklabels=[], yticklabels=[], zticklabels=[]
)
ax.set_proj_type("ortho")

curve_color = ["green", "darkviolet"]
projections_offset = 1.45
projections_alpha  = 0.0
plot_type = 'surface'

x_off = np.max(curves[:, 0, 0]) * projections_offset
y_off = np.max(curves[:, 0, 1]) * projections_offset
z_off = np.min(curves[:, 0, 2]) * projections_offset

for c in range(len(parameters_set)):
    x_off_new = np.max(curves[:, c, 0]) * projections_offset
    y_off_new = np.max(curves[:, c, 1]) * projections_offset
    z_off_new = np.min(curves[:, c, 2]) * projections_offset
    if x_off_new > x_off:
        x_off = x_off_new
    if y_off_new > y_off:
        y_off = y_off_new
    if z_off_new < z_off:
        z_off = z_off_new

for c, pset in enumerate(parameters_set):
    pvalue = pset["Dd"]

    ax.plot(curves[:, c, 0], curves[:, c, 1], curves[:, c, 2],
            color=curve_color[c], label=f"Dd={pvalue:.1f}")

    if plot_type == "contour":
      ax.plot(curves[:, c, 0], curves[:, c, 2],
              zs=y_off, zdir="y", color=curve_color[c],
              linestyle="--", alpha=projections_alpha,
      )
      ax.plot(curves[:, c, 1], curves[:, c, 2],
              zs=x_off, zdir="x", color=curve_color[c],
              linestyle="--", alpha=projections_alpha,
      )
    if plot_type == "surface":
        ax.plot_trisurf(curves[:, c, 0], curves[:, c, 1], curves[:, c, 2],
            color=curve_color[c], linewidth=0.3, antialiased=True, alpha=0.5
        )

if plot_type == "surface":
  #TODO: use Tx*Ty*Tz*{1,0,0}...
  K = parameters_set[1]["Kd"]
  D = parameters_set[1]["Dd"]
  x_points = np.linspace(-x_off, x_off)
  y_points = np.linspace(-y_off, y_off)
  ax.plot(0 * y_points, y_points, 0 * y_points,
          color="k", linestyle="--"
  )
  ax.plot(np.linspace(-x_off, x_off), np.zeros(50),
          K * np.linspace(-x_off, x_off), color="k", linestyle="--"
  )
  ax.plot(x_points, K/D * np.linspace(-x_off, x_off),
          K * x_points, color="k", linestyle="--"
  )

# Log from Pinocchio simulation
ax.plot(task_impedance_ts[:, 1],
        task_impedance_ts[:, 2],
        task_impedance_ts[:, 3],
        color="k", linestyle=":",
        alpha=0.0)

ax.xaxis.set_rotate_label(False)
ax.yaxis.set_rotate_label(False)
ax.zaxis.set_rotate_label(False)
ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
ax.set_ylabel("$\dot{e}_x$", fontdict=font)
ax.set_zlabel("$f_{ext}$", fontdict=font)
ax.set_xlabel("$e_x$", fontdict=font)
plt.legend(loc="upper center", fontsize="small",
           ncols=3, bbox_to_anchor=(0.5, 1.00)
)
plt.show(block=True)
