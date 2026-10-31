"""R14 figures. Light theme, unit-labelled axes, no smoothed presentation tricks."""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(R14_ROOT)
FIG = ROOT / "figures"
RES = ROOT / "results"
plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.25, "axes.edgecolor": "#666666",
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def scatter_panels() -> None:
    cv = pd.read_csv(RES / "sbli205_cv_predictions.csv")
    picks = [
        ("LOGO_x_bump", "dx_scp", "poly3", "Δx_scp, leave-one-position-out (cubic)"),
        ("LOGO_x_bump", "dy_scp", "gpr", "Δy_scp, leave-one-position-out (GPR)"),
        ("LOGO_h_bump", "dx_scp", "gpr", "Δx_scp, leave-one-height-out (GPR)"),
        ("LOGO_h_bump", "dy_scp", "gpr", "Δy_scp, leave-one-height-out (GPR)"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(8.2, 7.4))
    for ax, (sch, tgt, mdl, title) in zip(axes.ravel(), picks):
        s = cv[(cv.scheme == sch) & (cv.target == tgt) & (cv.model == mdl)]
        lim = [min(s.y_true.min(), s.y_pred.min()) - 0.3, max(s.y_true.max(), s.y_pred.max()) + 0.3]
        ax.plot(lim, lim, "--", color="#888888", lw=1, label="1:1")
        ax.scatter(s.y_true, s.y_pred, s=22, c="#b02418", edgecolor="white", lw=0.4, zorder=3)
        rmse = float(np.sqrt(np.mean((s.y_pred - s.y_true) ** 2)))
        ax.set_title(f"{title}\nRMSE = {rmse:.2f} mm", fontsize=8.5)
        ax.set_xlabel("measured [mm]")
        ax.set_ylabel("predicted [mm]")
        ax.set_xlim(lim); ax.set_ylim(lim)
        ax.legend(frameon=False, loc="upper left", fontsize=7)
    fig.suptitle("SBLI2.05 UQ: shock-crossing-point prediction, grouped cross-validation", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig01_sbli205_cv_scatter.png", bbox_inches="tight")
    plt.close(fig)


def surface_and_sensitivity() -> None:
    df = pd.read_csv(RES / "sbli205_cases.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0))
    ax = axes[0]
    hs = np.linspace(df.h_bump.min(), df.h_bump.max(), 60)
    xs = np.linspace(df.x_bump.min(), df.x_bump.max(), 60)
    H, Xg = np.meshgrid(hs, xs)
    coef, *_ = np.linalg.lstsq(
        np.c_[np.ones(len(df)), df.h_bump, df.x_bump, df.h_bump**2, df.x_bump**2,
              df.h_bump * df.x_bump, df.h_bump**3, df.x_bump**3,
              df.h_bump**2 * df.x_bump, df.h_bump * df.x_bump**2],
        df.dx_scp.to_numpy(), rcond=None)
    B = np.c_[np.ones(H.size), H.ravel(), Xg.ravel(), H.ravel()**2, Xg.ravel()**2,
              (H * Xg).ravel(), H.ravel()**3, Xg.ravel()**3,
              (H**2 * Xg).ravel(), (H * Xg**2).ravel()]
    Z = (B @ coef).reshape(H.shape)
    cs = ax.contourf(Xg, H, Z, levels=18, cmap="RdBu_r")
    ax.contour(Xg, H, Z, levels=8, colors="k", linewidths=0.3, alpha=0.5)
    ax.scatter(df.x_bump, df.h_bump, c=df.dx_scp, s=26, cmap="RdBu_r",
               edgecolor="k", lw=0.3, zorder=3)
    cb = fig.colorbar(cs, ax=ax)
    cb.set_label("Δx_scp [mm]")
    ax.set_xlabel("x_bump [mm]")
    ax.set_ylabel("h_bump [mm]")
    ax.set_title("Reconstructed cubic surface vs 45 measured cases", fontsize=9)

    ax = axes[1]
    for xv, g in df.groupby("x_bump"):
        g = g.sort_values("h_bump")
        ax.plot(g.h_bump, g.dx_scp, "o-", ms=3.2, lw=1.0,
                label=f"x={xv:.1f}")
    ax.set_xlabel("h_bump [mm]")
    ax.set_ylabel("Δx_scp [mm]")
    ax.set_title("Height sensitivity depends on bump position", fontsize=9)
    ax.legend(fontsize=6.4, ncol=2, frameon=False, title="x_bump [mm]")
    fig.tight_layout()
    fig.savefig(FIG / "fig02_sbli205_surface_sensitivity.png", bbox_inches="tight")
    plt.close(fig)


def pod_field() -> None:
    d = np.load(RES / "pod_example_fields.npz")
    X, Y = d["X"], d["Y"]
    fig, axes = plt.subplots(1, 4, figsize=(13.0, 3.3))
    vmin = float(np.nanpercentile(d["U_meas"], 2))
    vmax = float(np.nanpercentile(d["U_meas"], 98))
    for ax, arr, ttl in [
        (axes[0], d["U_meas"], "measured U"),
        (axes[1], d["U_pod"], "POD+GPR U"),
        (axes[2], d["U_meas"] - d["U_pod"], "residual U"),
    ]:
        if ttl.startswith("residual"):
            lim = float(np.nanpercentile(np.abs(arr), 98))
            im = ax.pcolormesh(X, Y, arr, cmap="RdBu_r", vmin=-lim, vmax=lim, shading="auto")
            ax.set_title(f"{ttl} (±{lim:.0f} m/s)", fontsize=8.5)
        else:
            im = ax.pcolormesh(X, Y, arr, cmap="viridis", vmin=vmin, vmax=vmax, shading="auto")
            ax.set_title(f"{ttl}", fontsize=8.5)
        fig.colorbar(im, ax=ax, fraction=0.046)
        ax.set_xlabel("X [mm]"); ax.set_ylabel("Y [mm]")
    ax = axes[3]
    m = d["mask"]
    ax.plot(d["U_meas"][m], d["U_pod"][m], ".", ms=1.2, color="#b02418", alpha=0.4)
    lim = [np.nanmin(d["U_meas"][m]), np.nanmax(d["U_meas"][m])]
    ax.plot(lim, lim, "--", color="#888888", lw=1)
    ax.set_xlabel("measured U [m/s]"); ax.set_ylabel("POD U [m/s]")
    ax.set_title(f"held-out case {int(d['case'])}, rank {int(d['rank'])}", fontsize=8.5)
    fig.suptitle("POD coefficient regression on an unseen bump position", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig03_pod_field_reconstruction.png", bbox_inches="tight")
    plt.close(fig)


def hmve_profiles() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from hmve_analysis import parse_file, RAW as HMVE_RAW

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.9))
    specs = [(axes[0], 16.0, "U"), (axes[1], 13.5, "U"), (axes[2], 16.0, "uu")]
    for ax, ang, field in specs:
        for f in sorted((HMVE_RAW / "axi").glob(f"PIVprofiles_M*_a{ang:g}_l0_Re1.dat")):
            mach = float(f.name.split("_M")[1].split("_")[0])
            df = parse_file(f)
            for st, ls in ((6, ":"), (16, "-"), (21, "--")):
                g = df[df.station == st].sort_values("y")
                if g.empty:
                    continue
                ax.plot(g[field], g.y, ls, lw=1.1, label=f"M{mach} st{st}")
        ax.set_ylabel("y [mm]")
        ax.set_xlabel("U/U1 [-]" if field == "U" else "uu/U1² [-]")
        ax.set_title(f"α = {ang}°, axisymmetric, Re-code 1", fontsize=9)
        ax.legend(fontsize=5.6, ncol=2, frameon=False)
        ax.set_ylim(0, 20)
    fig.suptitle("HMVE: wall-normal profiles upstream / at / downstream of the interaction", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig04_hmve_profiles.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    scatter_panels()
    surface_and_sensitivity()
    pod_field()
    hmve_profiles()
    print("figures written")
