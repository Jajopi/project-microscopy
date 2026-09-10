from sys import argv, stderr

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def get_image_size(image_file):
    with open(image_file, 'rb') as f:
        f.seek(16)
        width = int.from_bytes(f.read(4), 'big')
        height = int.from_bytes(f.read(4), 'big')
    return width, height

def merge_cluster_labels(labels):
    union_find = [i for i in range(len(labels))]
    def find(x):
        if union_find[x] != x: union_find[x] = find(union_find[x])
        return union_find[x]
    def union(x, y):
        root_x, root_y = find(x), find(y)
        union_find[max(root_x, root_y)] = min(root_x, root_y)

    single_labels = []
    single_indices = set()
    for i, label in enumerate(labels):
        is_root = False
        for j, other_label in enumerate(labels[i + 1:]):
            distance = ((label[0] - other_label[0]) ** 2 + (label[1] - other_label[1]) ** 2) ** 0.5
            if distance < label[2] / 4 + label[3] / 4 + other_label[2] / 4 + other_label[3] / 4:
                union(i, j + i + 1)
                is_root = True
        if not is_root and find(i) == i:
            single_labels.append(label)
            single_indices.add(i)

    cluster_boundaries = {}
    for i in range(len(labels)):
        if i in single_indices: continue
        root = find(i)
        if root not in cluster_boundaries:
            u, d, l ,r = labels[i][0] - labels[i][2] / 2, labels[i][0] + labels[i][2] / 2, labels[i][1] - labels[i][3] / 2, labels[i][1] + labels[i][3] / 2
            cluster_boundaries[root] = [u, d, l, r]
        else:
            u, d, l ,r = cluster_boundaries[root]
            cluster_boundaries[root] = [min(u, labels[i][0] - labels[i][2] / 2), max(d, labels[i][0] + labels[i][2] / 2), min(l, labels[i][1] - labels[i][3] / 2), max(r, labels[i][1] + labels[i][3] / 2)]
    cluster_labels = []
    for u, d, l, r in cluster_boundaries.values():
        cluster_labels.append(((u + d) / 2, (l + r) / 2, d - u, r - l))

    return cluster_labels, single_labels

def load_data(result_file, label_file, image_size):
    cluster_results = []
    single_results = []
    with open(result_file, 'r') as f:
        for raw_res in f.readlines()[1:]:
            vals = raw_res.strip().split(',')
            x, y = float(vals[2]) / image_size[0], float(vals[3]) / image_size[1]
            w, h = float(vals[7]) / image_size[0], float(vals[8]) / image_size[1]
            if vals[-1] == 'cluster': cluster_results.append((x, y, w, h))
            else: single_results.append((x, y, w, h))
    labels = []
    with open(label_file, 'r') as f:
        for raw_lab in f.readlines(): labels.append(tuple(map(float, raw_lab.strip().split()[1:])))
    cluster_labels, single_labels = merge_cluster_labels(labels)

    return cluster_results, single_results, cluster_labels, single_labels

def compare_results(results, labels):
    distances = []
    for i, label in enumerate(labels):
        for j, result in enumerate(results):
            distance = ((label[0] - result[0]) ** 2 + (label[1] - result[1]) ** 2) ** 0.5
            if distance > label[2] / 2 + label[3] / 2: continue
            distances.append((distance, i, j))
    distances.sort()

    used_labels = set()
    used_points = set()
    for distance, i, j in distances:
        if i in used_labels or j in used_points: continue
        used_labels.add(i)
        used_points.add(j)

    correct = [result for j, result in enumerate(results) if j in used_points]
    false_positives = [result for j, result in enumerate(results) if j not in used_points]
    false_negatives = [label for i, label in enumerate(labels) if i not in used_labels]

    TP, FP, FN = len(used_labels), len(results) - len(used_labels), len(labels) - len(used_labels)
    accuracy = TP / (TP + FP + FN) if TP + FP + FN > 0 else 0
    stats = len(labels), len(results), TP, FP, FN, accuracy
    return stats, correct, false_positives, false_negatives

def plot_comparison(cluster_correct, cluster_fp, cluster_fn, single_correct, single_fp, single_fn, image_size, image_file, output_path):
    width, height = image_size
    fig, ax = plt.subplots(figsize=(8, 8 * height / width))

    img = plt.imread(image_file)
    ax.imshow(img, extent=(0, 1, 0, 1), origin="lower", cmap="gray", alpha=1, zorder=0)

    def draw(boxes, color, tag):
        for x, y, w, h in boxes:
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, linewidth=1, edgecolor=color, facecolor="none", label=tag, alpha=0.5, zorder=2))

    draw(cluster_correct, "tab:blue", "cluster TP")
    draw(cluster_fp, "tab:cyan", "cluster FP")
    draw(cluster_fn, "tab:purple", "cluster FN")
    draw(single_correct, "tab:green", "single TP")
    draw(single_fp, "tab:orange", "single FP")
    draw(single_fn, "tab:red", "single FN")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.invert_yaxis()
    ax.set_aspect(height / width)

    handles, labels_ = ax.get_legend_handles_labels()
    by_tag = dict(zip(labels_, handles))
    ax.legend(by_tag.values(), by_tag.keys(), loc="upper right", fontsize="small")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

def print_stats(cluster_stats, single_stats):
    for i in range(len(cluster_stats)):
        if i == len(cluster_stats) - 1: print(f"{cluster_stats[i]:.2%}", end='\t')
        else: print(cluster_stats[i], end='\t')
    for i in range(len(single_stats)):
        if i == len(single_stats) - 1: print(f"{single_stats[i]:.2%}")
        else: print(single_stats[i], end='\t')

if __name__ == "__main__":
    result_file = argv[1]
    label_file = argv[2]
    image_file = argv[3]
    plot_file = argv[4] if len(argv) > 4 else None

    image_size = get_image_size(image_file)
    print(image_file, end='\t')
    cluster_results, single_results, cluster_labels, single_labels = load_data(result_file, label_file, image_size)
    cluster_stats, cluster_correct, cluster_fp, cluster_fn = compare_results(cluster_results, cluster_labels)
    single_stats, single_correct, single_fp, single_fn = compare_results(single_results, single_labels)
    print_stats(cluster_stats, single_stats)

    if plot_file: plot_comparison(cluster_correct, cluster_fp, cluster_fn, single_correct, single_fp, single_fn, image_size, image_file, plot_file)
