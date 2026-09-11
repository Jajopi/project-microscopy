from sys import argv

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

def load_data(result_file, label_file, image_size):
    results = []
    with open(result_file, 'r') as f:
        lines = f.readlines()
        header = lines[0].strip().split(',')
        x_idx, y_idx = header.index('X'), header.index('Y')
        w_idx, h_idx = header.index('Width'), header.index('Height')
        for raw_res in lines[1:]:
            vals = raw_res.strip().split(',')
            x, y = float(vals[x_idx]) / image_size[0], float(vals[y_idx]) / image_size[1]
            w, h = float(vals[w_idx]) / image_size[0], float(vals[h_idx]) / image_size[1]
            results.append((x, y, w, h))
    labels = []
    with open(label_file, 'r') as f:
        for raw_lab in f.readlines(): labels.append(tuple(map(float, raw_lab.strip().split()[1:])))

    return results, labels

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
    stats = len(labels), len(results), TP, FP, FN
    return stats, correct, false_positives, false_negatives

def plot_comparison(correct, false_positives, false_negatives, image_size, image_file, output_path):
    width, height = image_size
    fig, ax = plt.subplots(figsize=(8, 8 * height / width))

    img = plt.imread(image_file)
    ax.imshow(img, extent=(0, 1, 0, 1), origin="lower", cmap="gray", alpha=1, zorder=0)

    def draw(boxes, color, tag):
        for x, y, w, h in boxes:
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, linewidth=1, edgecolor=color, facecolor="none", label=tag, alpha=0.5, zorder=2))

    draw(correct, "tab:green", "TP")
    draw(false_positives, "tab:orange", "FP")
    draw(false_negatives, "tab:red", "FN")

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

def print_stats(stats): print('\t'.join(map(str, stats)))

if __name__ == "__main__":
    result_file = argv[1]
    label_file = argv[2]
    image_file = argv[3]
    plot_file = argv[4] if len(argv) > 4 else None

    image_size = get_image_size(image_file)
    print(image_file, end='\t')
    results, labels = load_data(result_file, label_file, image_size)
    stats, correct, false_positives, false_negatives = compare_results(results, labels)
    print_stats(stats)

    if plot_file:
        plot_comparison(correct, false_positives, false_negatives, image_size, image_file, plot_file)
