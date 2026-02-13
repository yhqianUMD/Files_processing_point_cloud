import csv
import re
import numpy as np
import shapely
from shapely.geometry import LineString
from shapely.strtree import STRtree
import time

SHAPELY2 = int(shapely.__version__.split(".")[0]) >= 2

WKT_RE = re.compile(
    r"LINESTRING\s*\(\s*([-\d.eE]+)\s+([-\d.eE]+)\s*,\s*([-\d.eE]+)\s+([-\d.eE]+)\s*\)"
)

def iter_lines_from_csv(csv_path):
    """Yield shapely LineString from CSV with 'geometry' column as WKT LINESTRING (x0 y0, x1 y1)."""
    with open(csv_path, "r", newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        if "geometry" not in reader.fieldnames:
            raise ValueError(f'Expected a "geometry" column. Got {reader.fieldnames}')
        for row in reader:
            wkt = row["geometry"]
            m = WKT_RE.search(wkt)
            if not m:
                continue
            x0, y0, x1, y1 = map(float, m.groups())
            yield LineString([(x0, y0), (x1, y1)])

def build_index(lines):
    """Build STRtree and keep a parallel list so we can map results back."""
    lines = list(lines)
    tree = STRtree(lines)
    return lines, tree

def matched_length_A_in_buffer_of_B(A_lines, B_lines, B_tree, buffer_dist):
    """
    Compute matched length: sum length( a ∩ buffer(union(nearby B), d) )
    Also returns total length of A.
    """
    total_A = 0.0
    matched = 0.0

    for a in A_lines:
        total_A += a.length

        # 1) spatial prefilter: bbox expanded by buffer_dist
        minx, miny, maxx, maxy = a.bounds
        query_env = shapely.box(minx - buffer_dist, miny - buffer_dist,
                                maxx + buffer_dist, maxy + buffer_dist)

        cand = B_tree.query(query_env)

        if len(cand) == 0:
            continue
        
        # Shapely 2 often returns indices, so convert to geometries. if it's indices, convert
        if isinstance(cand[0], (int, np.integer)):
            cand = [B_lines[i] for i in cand]

        # 2) local union + buffer only over nearby candidates
        #    (avoid global union/buffer)
        if SHAPELY2:
            u = shapely.union_all(cand)
            buf = shapely.buffer(u, buffer_dist)
            inter = shapely.intersection(a, buf)
            matched += shapely.length(inter)
        else:
            from shapely.ops import unary_union
            u = unary_union(cand)
            buf = u.buffer(buffer_dist)
            matched += a.intersection(buf).length

    return total_A, matched

def precision_recall_csv(reference_csv, extracted_csv, buffer_dist=0.5):
    # Build index on extracted for recall side
    extracted_lines, extracted_tree = build_index(iter_lines_from_csv(extracted_csv))
    reference_lines = list(iter_lines_from_csv(reference_csv))

    # Recall: how much reference is covered by extracted buffer
    L_R, M_R = matched_length_A_in_buffer_of_B(reference_lines, extracted_lines, extracted_tree, buffer_dist)
    recall = M_R / L_R if L_R > 0 else float("nan")

    # Build index on reference for precision side
    ref_lines, ref_tree = build_index(reference_lines)

    # Precision: how much extracted is covered by reference buffer
    L_E, M_E = matched_length_A_in_buffer_of_B(extracted_lines, ref_lines, ref_tree, buffer_dist)
    precision = M_E / L_E if L_E > 0 else float("nan")

    return {
        "buffer_dist": buffer_dist,
        "L_R_total_ref": L_R,
        "M_R_matched_ref": M_R,
        "recall_len_based": recall,
        "L_E_total_ext": L_E,
        "M_E_matched_ext": M_E,
        "precision_len_based": precision,
        "FN_len_missing_ref": max(0.0, L_R - M_R),
        "FP_len_extra_ext": max(0.0, L_E - M_E),
    }

# Example
if __name__ == "__main__":
    reference_csv = input("reference ridges CSV: ").strip()
    extracted_csv = input("extracted ridges CSV: ").strip()
    d = float(input("buffer distance (e.g. 0.5): ").strip())

    t_start = time.time()

    out = precision_recall_csv(reference_csv, extracted_csv, buffer_dist=d)
    for k, v in out.items():
        print(f"{k}: {v:.6f}" if isinstance(v, float) else f"{k}: {v}")
    
    t_end = time.time()
    print("Total time cost of this program:", t_end - t_start)
