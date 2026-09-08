from sys import argv, stderr

def get_image_size(image_file):
    with open(image_file, 'rb') as f:
        f.seek(16)
        width = int.from_bytes(f.read(4), 'big')
        height = int.from_bytes(f.read(4), 'big')
    return width, height

def load_data(result_file, label_file, image_size):
    results = []
    with open(result_file, 'r') as f:
        for raw_res in f.readlines()[1:]:
            vals = raw_res.strip().split(',')
            x, y = float(vals[2]) / image_size[0], float(vals[3]) / image_size[1]
            w, h = float(vals[7]) / image_size[0], float(vals[8]) / image_size[1]
            results.append((x, y, w, h))
    labels = []
    with open(label_file, 'r') as f:
        for raw_lab in f.readlines():
            labels.append(tuple(map(float, raw_lab.strip().split()[1:])))
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
        # print(f"{labels[i][0]:.4f},{results[j][0]:.4f}\t{labels[i][1]:.4f},{results[j][1]:.4f}\t{distance:.6f}", file=stderr)

    TP, FP, FN = len(used_labels), len(results) - len(used_labels), len(labels) - len(used_labels)
    accuracy = TP / (TP + FP + FN) if TP + FP + FN > 0 else 0
    print(f"{len(labels)}\t{len(results)}\t{TP}\t{FP}\t{FN}\t{accuracy:.2%}")

if __name__ == "__main__":
    result_file = argv[1]
    label_file = argv[2]
    image_file = argv[3]
    print(image_file, end='\t')
    results, labels = load_data(result_file, label_file, get_image_size(image_file))
    compare_results(results, labels)
