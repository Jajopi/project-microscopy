#!/usr/bin/env python3

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_stats import load_stats, hist, ratio, draw_sample_metrics, BINS_UNIT, BINS_FP

WORKFLOWS_DIR = "workflows"
OUTPUT_DIR = "plots"

def label_panel(ax, letter, workflow):
    ax.text(0.0, 1.15, f"{letter} {workflow}", transform=ax.transAxes, fontsize=16, fontweight="bold", va="bottom", ha="left")

def combine_histogram(clusters, simple, cellpose, key, label, color, filename, bins=BINS_UNIT, is_ratio=False):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), squeeze=False)

    def values(data):
        return ratio(data[key], data["labels"]) if is_ratio else data[key]

    hist(axes[0][0], values(clusters["single"]), bins, color, f"Single cell {label}", label)
    hist(axes[0][1], values(clusters["cluster"]), bins, color, f"Cluster {label}", label)
    hist(axes[1][0], values(simple["single"]), bins, color, f"Single cell {label}", label)
    hist(axes[1][1], values(cellpose["single"]), bins, color, f"Single cell {label}", label)

    label_panel(axes[0][0], "a)", "clusters")
    label_panel(axes[1][0], "b)", "simple")
    label_panel(axes[1][1], "c)", "cellpose")

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close(fig)

def combine_sample_metrics(clusters, simple, cellpose):
    fig, axes = plt.subplots(2, 2, figsize=(20, 14), squeeze=False, gridspec_kw={"hspace": 0.6})

    draw_sample_metrics(axes[0][0], clusters["single"], "Single cell metrics by sample")
    draw_sample_metrics(axes[0][1], clusters["cluster"], "Cluster metrics by sample")
    draw_sample_metrics(axes[1][0], simple["single"], "Single cell metrics by sample")
    draw_sample_metrics(axes[1][1], cellpose["single"], "Single cell metrics by sample")

    label_panel(axes[0][0], "a)", "clusters")
    label_panel(axes[1][0], "b)", "simple")
    label_panel(axes[1][1], "c)", "cellpose")

    fig.savefig(os.path.join(OUTPUT_DIR, "metrics_by_sample.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    clusters_single, clusters_cluster = load_stats(os.path.join(WORKFLOWS_DIR, "clusters"))
    simple_single, _ = load_stats(os.path.join(WORKFLOWS_DIR, "simple"))
    cellpose_single, _ = load_stats(os.path.join(WORKFLOWS_DIR, "cellpose"))

    clusters = {"single": clusters_single, "cluster": clusters_cluster}
    simple = {"single": simple_single}
    cellpose = {"single": cellpose_single}

    combine_histogram(clusters, simple, cellpose, "accuracy", "Accuracy", "tab:green", "accuracy_histogram.png")
    combine_histogram(clusters, simple, cellpose, "precision", "Precision", "tab:blue", "precision_histogram.png")
    combine_histogram(clusters, simple, cellpose, "recall", "Recall", "tab:purple", "recall_histogram.png")
    combine_histogram(clusters, simple, cellpose, "f1", "F1 score", "tab:brown", "f1_histogram.png")

    combine_histogram(clusters, simple, cellpose, "FP", "FP / labels", "tab:orange", "fp_ratio_histogram.png", bins=BINS_FP, is_ratio=True)
    combine_histogram(clusters, simple, cellpose, "FN", "FN / labels", "tab:red", "fn_ratio_histogram.png", bins=BINS_UNIT, is_ratio=True)

    combine_sample_metrics(clusters, simple, cellpose)
