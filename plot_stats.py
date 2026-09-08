#!/usr/bin/env python3

import csv
import os
from sys import argv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BINS_UNIT = [i / 10 for i in range(11)]  # 0.0 .. 1.0, step 0.1
BINS_FP = [i / 10 for i in range(21)]    # 0.0 .. 2.0, step 0.1

def load_stats(workflow_dir):
    with open(os.path.join(workflow_dir, "stats.csv"), newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        rows = [row for row in reader if row]

    has_clusters = len(header) > 7

    def extract(offset):
        data = {"labels": [], "identified": [], "TP": [], "FP": [], "FN": [], "accuracy": []}
        for row in rows:
            data["labels"].append(float(row[offset]))
            data["identified"].append(float(row[offset + 1]))
            data["TP"].append(float(row[offset + 2]))
            data["FP"].append(float(row[offset + 3]))
            data["FN"].append(float(row[offset + 4]))
            data["accuracy"].append(float(row[offset + 5].rstrip('%')) / 100)
        return data

    single = extract(7 if has_clusters else 1)
    cluster = extract(1) if has_clusters else None

    return single, cluster

def ratio(counts, labels):
    return [count / label for count, label in zip(counts, labels) if label > 0]

def hist(ax, values, edges, color, title, xlabel):
    clipped = [min(v, edges[-1]) for v in values]
    ax.hist(clipped, bins=edges, color=color, edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Number of images")

def plot_accuracy_histogram(single, cluster, output_dir):
    has_clusters = cluster is not None
    fig, axes = plt.subplots(1, 2 if has_clusters else 1, figsize=(6 * (2 if has_clusters else 1), 5), squeeze=False)

    hist(axes[0][0], single["accuracy"], BINS_UNIT, "tab:green", "Single cell accuracy", "Accuracy")
    if has_clusters:
        hist(axes[0][1], cluster["accuracy"], BINS_UNIT, "tab:blue", "Cluster accuracy", "Accuracy")

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "accuracy_histogram.png"), dpi=150)
    plt.close(fig)

def plot_fp_fn_ratio_histograms(single, cluster, output_dir):
    has_clusters = cluster is not None
    fig, axes = plt.subplots(2, 2 if has_clusters else 1, figsize=(6 * (2 if has_clusters else 1), 10), squeeze=False)

    hist(axes[0][0], ratio(single["FP"], single["labels"]), BINS_FP, "tab:orange", "Single cell FP / labels", "FP / labels")
    hist(axes[1][0], ratio(single["FN"], single["labels"]), BINS_UNIT, "tab:red", "Single cell FN / labels", "FN / labels")

    if has_clusters:
        hist(axes[0][1], ratio(cluster["FP"], cluster["labels"]), BINS_FP, "tab:orange", "Cluster FP / labels", "FP / labels")
        hist(axes[1][1], ratio(cluster["FN"], cluster["labels"]), BINS_UNIT, "tab:red", "Cluster FN / labels", "FN / labels")

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "fp_fn_ratio_histogram.png"), dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    workflow_dir = argv[1]
    single, cluster = load_stats(workflow_dir)
    plot_accuracy_histogram(single, cluster, workflow_dir)
    plot_fp_fn_ratio_histograms(single, cluster, workflow_dir)
