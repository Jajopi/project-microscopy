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

    has_clusters = len(header) > 6

    def extract(offset):
        TP = [float(row[offset + 2]) for row in rows]
        FP = [float(row[offset + 3]) for row in rows]
        FN = [float(row[offset + 4]) for row in rows]

        accuracy = [tp / (tp + fp + fn) if tp + fp + fn > 0 else 0 for tp, fp, fn in zip(TP, FP, FN)]
        precision = [tp / (tp + fp) if tp + fp > 0 else 0 for tp, fp in zip(TP, FP)]
        recall = [tp / (tp + fn) if tp + fn > 0 else 0 for tp, fn in zip(TP, FN)]
        f1 = [2 * p * r / (p + r) if p + r > 0 else 0 for p, r in zip(precision, recall)]

        return {
            "labels": [float(row[offset]) for row in rows],
            "identified": [float(row[offset + 1]) for row in rows],
            "TP": TP, "FP": FP, "FN": FN,
            "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1,
        }

    single = extract(6 if has_clusters else 1)
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

def plot_metric_histogram(single, cluster, output_dir, key, label, color, filename):
    has_clusters = cluster is not None
    fig, axes = plt.subplots(1, 2 if has_clusters else 1, figsize=(6 * (2 if has_clusters else 1), 5), squeeze=False)

    hist(axes[0][0], single[key], BINS_UNIT, color, f"Single cell {label}", label)
    if has_clusters:
        hist(axes[0][1], cluster[key], BINS_UNIT, color, f"Cluster {label}", label)

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, filename), dpi=150)
    plt.close(fig)

def plot_ratio_histogram(single, cluster, output_dir, count_key, bins, color, label, filename):
    has_clusters = cluster is not None
    fig, axes = plt.subplots(1, 2 if has_clusters else 1, figsize=(6 * (2 if has_clusters else 1), 5), squeeze=False)

    hist(axes[0][0], ratio(single[count_key], single["labels"]), bins, color, f"Single cell {label}", label)
    if has_clusters:
        hist(axes[0][1], ratio(cluster[count_key], cluster["labels"]), bins, color, f"Cluster {label}", label)

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, filename), dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    workflow_dir = argv[1]
    single, cluster = load_stats(workflow_dir)

    plot_metric_histogram(single, cluster, workflow_dir, "accuracy", "Accuracy", "tab:green", "accuracy_histogram.png")
    plot_metric_histogram(single, cluster, workflow_dir, "precision", "Precision", "tab:blue", "precision_histogram.png")
    plot_metric_histogram(single, cluster, workflow_dir, "recall", "Recall", "tab:purple", "recall_histogram.png")
    plot_metric_histogram(single, cluster, workflow_dir, "f1", "F1 score", "tab:brown", "f1_histogram.png")

    plot_ratio_histogram(single, cluster, workflow_dir, "FP", BINS_FP, "tab:orange", "FP / labels", "fp_ratio_histogram.png")
    plot_ratio_histogram(single, cluster, workflow_dir, "FN", BINS_UNIT, "tab:red", "FN / labels", "fn_ratio_histogram.png")
