# -*- coding: utf-8 -*-
"""
Lego színfelismerő: 4x3-as fekete keretben lévő Lego lapok színeinek
felismerése (kék, zöld, fehér, sárga) kameraképről.

Fázisok (mindegyikről mentés készül az output/<képnév>/ könyvtárba):
  1. eredeti kép
  2. fehéregyensúly-korrigált kép
  3. sötét (fekete keret) maszk
  4. keret kontúrja és a 4 sarokpont
  5. perspektív-korrigált (felülnézeti) kép
  6. cella-mintavételi területek a mért HSV értékekkel
  7. végeredmény a felismert színekkel

Használat:
  python color_detect.py --train          # betanulás az images/ képekből
  python color_detect.py                  # az images/ könyvtár összes képe
  python color_detect.py images/capture3.jpg
"""

import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

# A rács mérete: 4 oszlop x 3 sor
GRID_COLS = 4
GRID_ROWS = 3

# A felülnézeti (warpolt) kép mérete - a keret valós oldalaránya kb. 4:3
WARP_W = 800
WARP_H = 600

# A keret szegélyének aránya a warpolt képen (külső szél -> első cella széle)
MARGIN_X = 0.075
MARGIN_Y = 0.095

# A cella közepén mintavételezett négyzet fél-oldala a cellaméret arányában
PATCH_RATIO = 0.30

OUTPUT_DIR = Path(__file__).parent / "output"
MODEL_PATH = Path(__file__).parent / "lego_colors.json"

# A tanítóképeken lévő (ismert) elrendezés a betanuláshoz
GROUND_TRUTH = [
    ["kek", "sarga", "kek", "zold"],
    ["feher", "zold", "feher", "sarga"],
    ["kek", "sarga", "kek", "zold"],
]

# Magyar színnevek és a hozzájuk tartozó BGR a kirajzoláshoz
COLOR_BGR = {
    "kek": (255, 80, 0),
    "zold": (0, 160, 0),
    "feher": (255, 255, 255),
    "sarga": (0, 220, 255),
    "ismeretlen": (0, 0, 255),
}


def white_balance(img, save):
    """Fehéregyensúly-korrekció a kép világos, alacsony telítettségű
    pixelei (fehér papír háttér) alapján, így a kamera színezete
    (pl. kékes árnyalat) nem zavarja a színosztályozást."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s, v = hsv[..., 1], hsv[..., 2]

    # Világos, de nem beégett pixelek
    bright = (v > 170) & (v < 250)
    if bright.sum() < 500:
        bright = v > np.percentile(v, 90)
    # Közülük a legkevésbé telítettek (a tényleg fehér felületek)
    sat_thr = np.percentile(s[bright], 30)
    ref = bright & (s <= sat_thr)

    med = np.median(img[ref], axis=0)  # B, G, R medián a fehér referencián
    scale = np.clip(med.mean() / np.maximum(med, 1), 0.6, 1.7)
    balanced = np.clip(img.astype(np.float32) * scale, 0, 255).astype(np.uint8)
    save("02_feheregyensuly", balanced)
    return balanced


def order_corners(pts):
    """4 pont rendezése: bal-felső, jobb-felső, jobb-alsó, bal-alsó."""
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array(
        [
            pts[np.argmin(s)],  # bal-felső: x+y minimális
            pts[np.argmin(d)],  # jobb-felső: y-x minimális
            pts[np.argmax(s)],  # jobb-alsó: x+y maximális
            pts[np.argmax(d)],  # bal-alsó: y-x maximális
        ],
        dtype=np.float32,
    )


def quad_from_contour(contour):
    """A kontúr konvex burkának közelítése 4 sarokpontra."""
    hull = cv2.convexHull(contour)
    peri = cv2.arcLength(hull, True)
    for eps in np.linspace(0.01, 0.1, 30):
        approx = cv2.approxPolyDP(hull, eps * peri, True)
        if len(approx) == 4:
            return approx.reshape(4, 2).astype(np.float32)
    return cv2.boxPoints(cv2.minAreaRect(contour))


def bar_median(warped):
    """A keretbordák (a cellák közötti és körüli keretterület) medián
    BGR színe a kiterített képen."""
    centers, cell_w, cell_h = cell_centers()
    bar_mask = np.full((WARP_H, WARP_W), 255, np.uint8)
    for _, _, cx, cy in centers:
        cv2.rectangle(bar_mask,
                      (int(cx - cell_w * 0.62), int(cy - cell_h * 0.62)),
                      (int(cx + cell_w * 0.62), int(cy + cell_h * 0.62)),
                      0, -1)
    return np.median(warped[bar_mask > 0], axis=0)


def grid_score(img, corners):
    """Megméri, mennyire rácsszerű a kép tartalma az adott sarokpontokkal
    kiterítve: jó sarkok esetén a cellahelyeken (színes vagy fehér Lego
    lap) a medián szín erősen eltér a köztük lévő keretbordák szürke
    mediánszínétől. A pontszám az átlagos színtávolság."""
    dst = np.array(
        [[0, 0], [WARP_W - 1, 0], [WARP_W - 1, WARP_H - 1], [0, WARP_H - 1]],
        dtype=np.float32,
    )
    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(img, M, (WARP_W, WARP_H))

    centers, cell_w, cell_h = cell_centers()
    bar_med = bar_median(warped)

    px, py = int(cell_w * 0.25), int(cell_h * 0.25)
    dists = []
    for _, _, cx, cy in centers:
        cell = warped[cy - py:cy + py, cx - px:cx + px].reshape(-1, 3)
        cell_med = np.median(cell, axis=0)
        dists.append(np.linalg.norm(cell_med - bar_med))
    return float(np.mean(dists))


def find_frame_corners(img, save):
    """Megkeresi a fekete keret 4 sarokpontját.

    Több maszkváltozatot próbál végig (különböző sötétségi küszöbök,
    illetve sötét VAGY telített pixelek a csillogó keretrészekhez), és
    azt a jelöltet választja, amelyiknél a kiterített kép a leginkább
    rácsszerű (grid_score). Közben menti a maszkot és a kontúros képet."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    saturated = ((hsv[..., 1] > 100) & (hsv[..., 2] > 60)).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))

    # Maszkváltozatok: lokálisan sötét (adaptív küszöb, csillogó keretre is
    # működik), illetve globális sötétségi küszöbök; mindkettő a telített
    # (Lego-színű) pixelekkel kiegészítve is
    adaptive = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY_INV, 51, 10)
    mask_variants = [adaptive, cv2.bitwise_or(adaptive, saturated)]
    for thr in (70, 90, 110, 130, 150):
        _, dark = cv2.threshold(blur, thr, 255, cv2.THRESH_BINARY_INV)
        mask_variants.append(dark)
        mask_variants.append(cv2.bitwise_or(dark, saturated))

    best = None  # (pontszám, kontúr, sarkok, maszk)
    for mask0 in mask_variants:
        # A cellák és a keret egy tömbbé olvasztása, zaj eltávolítása
        mask = cv2.morphologyEx(mask0, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if not 0.03 * w * h < area < 0.6 * w * h:
                continue
            x, y, bw, bh = cv2.boundingRect(c)
            # A kép szélét érintő sötét sávok (pl. ablak) kizárása
            if x <= 2 or y <= 2 or x + bw >= w - 2 or y + bh >= h - 2:
                continue
            corners = quad_from_contour(c)
            # Oldalarány: a keret kb. 4:3, vékony csíkok kizárása
            e1 = (np.linalg.norm(corners[0] - corners[1]) +
                  np.linalg.norm(corners[2] - corners[3])) / 2
            e2 = (np.linalg.norm(corners[1] - corners[2]) +
                  np.linalg.norm(corners[3] - corners[0])) / 2
            if max(e1, e2) / max(min(e1, e2), 1) > 4.0:
                continue
            ordered = order_corners(corners)
            score = grid_score(img, ordered)
            if best is None or score > best[0]:
                best = (score, c, ordered, mask)

    if best is None or best[0] < 50:
        return None
    _, contour, corners, mask = best
    save("03_maszk", mask)

    vis = img.copy()
    cv2.drawContours(vis, [contour], -1, (0, 255, 0), 2)
    for i, (x, y) in enumerate(corners):
        cv2.circle(vis, (int(x), int(y)), 8, (0, 0, 255), -1)
        cv2.putText(vis, str(i), (int(x) + 10, int(y) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    save("04_kontur", vis)
    return corners


def warp_topdown(img, corners, save):
    """Perspektív transzformáció felülnézetbe."""
    dst = np.array(
        [[0, 0], [WARP_W - 1, 0], [WARP_W - 1, WARP_H - 1], [0, WARP_H - 1]],
        dtype=np.float32,
    )
    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(img, M, (WARP_W, WARP_H))
    save("05_felulnezet", warped)
    return warped


def chroma(bgr):
    """Megvilágítás erősségétől független színarányok (B, G, R)."""
    b, g, r = (float(x) for x in bgr)
    total = max(b + g + r, 1.0)
    return np.array([3 * b / total, 3 * g / total, 3 * r / total])


def bgr_to_feature(bgr, bar_bgr):
    """Egy cella medián BGR színéből jellemzővektort képez:
    - kromatikusság (megvilágítástól független színarányok),
    - a keretbordák színéhez viszonyított kromatikusság (a borda
      semleges műanyag, így a különbség a kamera színezetétől
      függetlenül a lap tényleges színét tükrözi),
    - fényerő."""
    c = chroma(bgr)
    rel = c - chroma(bar_bgr)
    v = max(float(x) for x in bgr) / 255.0
    return np.concatenate([c, 2.0 * rel, [0.7 * v]])


def classify_hsv(h, s, v):
    """Tartalék szabály-alapú osztályozó, ha még nincs betanított modell."""
    if s < 60 and v > 110:
        return "feher"
    if 15 <= h <= 39:
        return "sarga"
    if 40 <= h <= 95:
        return "zold"
    if 96 <= h <= 135:
        return "kek"
    return "ismeretlen"


def classify_knn(bgr, bar_bgr, model, k=5):
    """A betanult minták közül a k legközelebbi alapján dönt,
    távolsággal fordítottan súlyozott szavazással (így egy nagyon
    közeli minta többet nyom a latban, mint több távolabbi)."""
    feat = bgr_to_feature(bgr, bar_bgr)
    dists = np.linalg.norm(model["features"] - feat, axis=1)
    nearest = np.argsort(dists)[:k]
    votes = {}
    for i in nearest:
        label = model["labels"][i]
        votes[label] = votes.get(label, 0) + 1.0 / (dists[i] + 1e-6)
    return max(votes, key=votes.get)


def cell_centers():
    """A 12 cella középpontja és a cellaméret a warpolt képen."""
    inner_w = WARP_W * (1 - 2 * MARGIN_X)
    inner_h = WARP_H * (1 - 2 * MARGIN_Y)
    cell_w = inner_w / GRID_COLS
    cell_h = inner_h / GRID_ROWS
    centers = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cx = int(WARP_W * MARGIN_X + (c + 0.5) * cell_w)
            cy = int(WARP_H * MARGIN_Y + (r + 0.5) * cell_h)
            centers.append((r, c, cx, cy))
    return centers, cell_w, cell_h


def sample_cells(warped, save):
    """A 4x3 rács celláinak mintavételezése: cellánként a medián BGR és
    HSV érték (a sötét keret-/árnyékpixelek kihagyásával)."""
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
    centers, cell_w, cell_h = cell_centers()
    px = int(cell_w * PATCH_RATIO)
    py = int(cell_h * PATCH_RATIO)

    vis = warped.copy()
    samples = {}
    for r, c, cx, cy in centers:
        patch_bgr = warped[cy - py:cy + py, cx - px:cx + px].reshape(-1, 3)
        patch_hsv = hsv[cy - py:cy + py, cx - px:cx + px].reshape(-1, 3)
        # A becsúszó keretdarabok és árnyékok (sötét pixelek) kihagyása
        keep = patch_hsv[:, 2] > 60
        if keep.sum() < 0.2 * len(patch_hsv):
            keep[:] = True
        med_bgr = np.median(patch_bgr[keep], axis=0)
        med_hsv = np.median(patch_hsv[keep], axis=0)
        samples[(r, c)] = (med_bgr, med_hsv)

        cv2.rectangle(vis, (cx - px, cy - py), (cx + px, cy + py),
                      (0, 0, 255), 2)
        mh, ms, mv = med_hsv
        cv2.putText(vis, f"H{mh:.0f} S{ms:.0f} V{mv:.0f}",
                    (cx - px, cy - py - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
    save("06_cellak", vis)
    return samples, bar_median(warped)


def classify_cells(samples, bar_med, model):
    """Cellánkénti színosztályozás: betanult modellel k-NN,
    anélkül szabály-alapú HSV küszöbökkel."""
    grid = [["ismeretlen"] * GRID_COLS for _ in range(GRID_ROWS)]
    for (r, c), (med_bgr, med_hsv) in samples.items():
        if model is not None:
            grid[r][c] = classify_knn(med_bgr, bar_med, model)
        else:
            grid[r][c] = classify_hsv(*med_hsv)
    return grid


def draw_result(warped, grid, save):
    """Végeredmény: cellák felirattal és színes kerettel."""
    centers, cell_w, cell_h = cell_centers()
    result = warped.copy()
    for r, c, cx, cy in centers:
        name = grid[r][c]
        bgr = COLOR_BGR[name]
        cv2.rectangle(result,
                      (int(cx - cell_w * 0.4), int(cy - cell_h * 0.4)),
                      (int(cx + cell_w * 0.4), int(cy + cell_h * 0.4)),
                      bgr, 3)
        cv2.putText(result, name, (int(cx - cell_w * 0.35), cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
        cv2.putText(result, name, (int(cx - cell_w * 0.35), cy + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr, 2)
    save("07_eredmeny", result)


def load_model():
    """Betanított színminták betöltése, ha vannak."""
    if not MODEL_PATH.exists():
        return None
    data = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    return {
        "features": np.array(data["features"]),
        "labels": data["labels"],
    }


def process_image(img):
    """Egy kép teljes feldolgozása; visszaadja a 4x3-as színmátrixot
    és a cellánkénti mintákat (a tanításhoz)."""

    model = load_model()
    out_dir = OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    def save(name, image):
        cv2.imwrite(str(out_dir / f"{name}.jpg"), image)

    save("01_eredeti", img)

    balanced = white_balance(img, save)
    corners = find_frame_corners(balanced, save)
    if corners is None:
        print("A keret nem található!")
        return None, None

    warped = warp_topdown(balanced, corners, save)
    samples, bar_med = sample_cells(warped, save)
    grid = classify_cells(samples, bar_med, model)
    draw_result(warped, grid, save)

    # for row in grid:
    #     print("  " + "  ".join(f"{name:<10}" for name in row))
    return grid, (samples, bar_med)


