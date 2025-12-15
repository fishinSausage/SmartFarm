import cv2
import numpy as np

# ---------- Tunable parameters ----------
RESIZE_WIDTH  = 640
RESIZE_HEIGHT = 480

# Area thresholds (in pixels) – must be tuned for your camera height
# far away plant
# MIN_AREA_VALID = 80     # below this: ignore as noise
# MIN_AREA_TINY  = 300    # below this: "tiny/missing"
# BIG_PLANT_AREA = 800    # above this: considered "big"

# TODO close up plant
MIN_AREA_VALID = 1000     # ignore anything smaller than this
MIN_AREA_TINY  = 2500     # below this: tiny/missing
BIG_PLANT_AREA = 25000     # above this: big plant

# Green ratio thresholds
GREEN_RATIO_HEALTHY   = 0.7   # >= this: mostly green
GREEN_RATIO_MILD      = 0.4   # between this and healthy: partially browned
# ----------------------------------------


def get_total_plant_mask(bgr_img):
    """
    Detect all plant-colored pixels (green + yellowish/brownish lettuce)
    using HSV. Returns a binary mask (uint8 0/255).
    """
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # HSV ranges need to be tuned for your lighting + lettuce type.
    # Rough ranges:
    #   - green:  H 35–85
    #   - yellow: H 20–35
    # We'll combine them so both healthy green and stressed yellow leaves
    # are counted as "plant".
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    lower_yellow = np.array([28, 40, 80])
    upper_yellow = np.array([38, 255, 255])

    mask_green  = cv2.inRange(hsv, lower_green,  upper_green)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    mask_plant_total = cv2.bitwise_or(mask_green, mask_yellow)

    # Morphological cleanup
    kernel = np.ones((5, 5), np.uint8)
    mask_plant_total = cv2.morphologyEx(mask_plant_total, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_plant_total = cv2.morphologyEx(mask_plant_total, cv2.MORPH_CLOSE, kernel, iterations=1)

    return mask_plant_total


def compute_exg_green_mask(bgr_img, plant_mask_total):
    """
    Compute ExG image and a STRICT green-only mask (healthy green parts).
    Uses BOTH HSV (pure green hue) and a fixed ExG threshold.
    """
    # extract hsv green mask
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    lower_hsv_green = np.array([35, 40, 40])
    upper_hsv_green = np.array([85, 255, 255])
    hsv_green_mask = cv2.inRange(hsv, lower_hsv_green, upper_hsv_green)

    # exg calculation for each pixel
    b, g, r = cv2.split(bgr_img.astype(np.float32) / 255.0)
    exg = 2 * g - r - b

    # normalize
    exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX)
    exg_uint8 = exg_norm.astype(np.uint8)
    exg_inside_plant = exg_uint8.copy()
    exg_inside_plant[plant_mask_total == 0] = 0

    # apply ExG threshold to all pixels
    EXG_STRICT_THRESHOLD = 140
    _, exg_strict_mask = cv2.threshold(
        exg_inside_plant, EXG_STRICT_THRESHOLD, 255, cv2.THRESH_BINARY
    )

    # combine HSV green and strong ExG 
    mask_green = cv2.bitwise_and(exg_strict_mask, hsv_green_mask)

    # Optional cleanup
    kernel = np.ones((3, 3), np.uint8)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel, iterations=1)

    return exg_uint8, mask_green



# crop_inspection_v2.py

def analyze_plants(bgr_img, lettuce_mask=None):
    """
    Main analysis:
      - detect plant regions
      - compute total area, green area, green_ratio
      - classify health/size

    If lettuce_mask is given (uint8 0/255 same size as bgr_img),
    we only analyze pixels that YOLO marked as lettuce.
    """
    resized = cv2.resize(bgr_img, (RESIZE_WIDTH, RESIZE_HEIGHT))

    # If we have a lettuce mask from YOLO, resize it to our working size
    if lettuce_mask is not None:
        lettuce_mask_resized = cv2.resize(
            lettuce_mask,
            (RESIZE_WIDTH, RESIZE_HEIGHT),
            interpolation=cv2.INTER_NEAREST
        )
    else:
        lettuce_mask_resized = None

    # 1) Get total plant mask (all plant-colored tissue)
    plant_mask_total = get_total_plant_mask(resized)

    # Restrict to YOLO lettuces only
    if lettuce_mask_resized is not None:
        plant_mask_total = cv2.bitwise_and(plant_mask_total, lettuce_mask_resized)

    # 2) Get ExG and green-only mask (healthy green parts) – now only inside YOLO lettuce areas
    exg_img, mask_green = compute_exg_green_mask(resized, plant_mask_total)

    # 3) Connected components on TOTAL plant mask (already restricted)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        plant_mask_total, connectivity=8
    )

    plants = []
    for i in range(1, num_labels):
        x, y, w, h, area_total = stats[i]

        if area_total < MIN_AREA_VALID:
            continue

        region_total_mask = (labels == i)
        total_plant_pixels = int(np.count_nonzero(region_total_mask))
        green_pixels = int(np.count_nonzero(
            (mask_green == 255) & region_total_mask
        ))

        if total_plant_pixels == 0:
            green_ratio = 0.0
        else:
            green_ratio = green_pixels / total_plant_pixels

        cx, cy = centroids[i]

        region_exg_vals = exg_img[(mask_green == 255) & region_total_mask]
        mean_exg_green = float(region_exg_vals.mean()) if region_exg_vals.size > 0 else 0.0

        # classification logic unchanged...
        if total_plant_pixels < MIN_AREA_TINY:
            label = "tiny/missing"
            color = (200, 200, 200)
        else:
            is_big = total_plant_pixels >= BIG_PLANT_AREA
            if green_ratio >= GREEN_RATIO_HEALTHY:
                label = "big_healthy" if is_big else "small_healthy"
                color = (0, 255, 0)
            else:
                label = "big_stressed" if is_big else "small_stressed"
                color = (0, 0, 255)

        plants.append({
            "id": i,
            "bbox": (x, y, w, h),
            "centroid": (int(cx), int(cy)),
            "area_total": int(total_plant_pixels),
            "green_pixels": int(green_pixels),
            "green_ratio": float(green_ratio),
            "mean_exg_green": mean_exg_green,
            "label": label,
            "color": color
        })

    return resized, exg_img, plant_mask_total, mask_green, plants


def visualize_results(resized, plants):
    """
    Draw colored circles / boxes and labels on the image.
    """
    vis = resized.copy()

    for p in plants:
        cx, cy = p["centroid"]
        x, y, w, h = p["bbox"]
        color = p["color"]
        label = p["label"]

        # Bounding box
        cv2.rectangle(vis, (x, y), (x + w, y + h), color, 1)

        # Centroid marker
        cv2.circle(vis, (cx, cy), 10, color, 2)

        # Text label
        cv2.putText(
            vis, label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, color, 1, cv2.LINE_AA
        )

    return vis


# -------- Example test harness --------
if __name__ == "__main__":
    # For now, test with an image file.
    # On the Pi you'll replace this with a camera capture.
    frame = cv2.imread("lettuce_bed.jpg")
    # frame = cv2.imread("bad_lettuce.jpg")
    # frame = cv2.imread("very_bad_lettuce.jpg")
    if frame is None:
        raise RuntimeError("Could not read lettuce_bed.jpg")

    resized, exg_img, plant_mask_total, mask_green, plants = analyze_plants(frame)
    vis = visualize_results(resized, plants)

    print("Detected plants:")
    for p in plants:
        print(
            f"ID {p['id']}: area_total={p['area_total']}, "
            f"green_pixels={p['green_pixels']}, "
            f"green_ratio={p['green_ratio']:.2f}, "
            f"mean_exg_green={p['mean_exg_green']:.1f}, "
            f"label={p['label']}"
        )




    cv2.imwrite("resized.jpg", resized)
    cv2.imwrite("plant_mask_total.jpg", plant_mask_total) 
    cv2.imwrite("mask_green.jpg", mask_green)
    cv2.imwrite("ExG.jpg", exg_img)
    cv2.imwrite("health_visualization.jpg", vis)

    print("Saved: resized.jpg, exg.jpg, mask.jpg, health_vis.jpg")
