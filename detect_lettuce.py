# detect_lettuce.py
import onnxruntime as ort
import numpy as np
import cv2

session = ort.InferenceSession(
    "best.onnx",
    providers=["CPUExecutionProvider"]
)

def letterbox(im, new_shape=320, color=(114, 114, 114)):
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    shape = im.shape[:2]  # (h, w)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))  # (w, h)

    dw = new_shape[1] - new_unpad[0]
    dh = new_shape[0] - new_unpad[1]
    dw /= 2
    dh /= 2

    im_resized = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im_padded = cv2.copyMakeBorder(
        im_resized, top, bottom, left, right,
        cv2.BORDER_CONSTANT, value=color
    )

    return im_padded, r, dw, dh

def preprocess_frame(bgr_img, img_size=320):
    img_h, img_w = bgr_img.shape[:2]
    img, r, dw, dh = letterbox(bgr_img, img_size)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    blob = np.transpose(img, (2, 0, 1))
    blob = np.expand_dims(blob, axis=0)
    return blob, r, dw, dh, img_w, img_h

def postprocess(predictions, r, dw, dh, img_w, img_h, conf_threshold=0.25, iou_threshold=0.45):
    preds = predictions[0].T

    results_xyxy = []

    for row in preds:
        x, y, w, h, conf, cls = row  # assuming cls is last element
        if conf < conf_threshold:
            continue

        x = (x - dw) / r
        y = (y - dh) / r
        w = w / r
        h = h / r

        x1 = x - w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2

        results_xyxy.append([x1, y1, x2, y2, conf, cls])

    if len(results_xyxy) > 0:
        results_xyxy = np.array(results_xyxy)
        boxes = results_xyxy[:, :4].astype(np.float32)
        scores = results_xyxy[:, 4].astype(np.float32)

        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            conf_threshold,
            iou_threshold
        )

        if len(indices) > 0:
            if isinstance(indices, np.ndarray):
                indices = indices.flatten()
            elif isinstance(indices, (list, tuple)):
                indices = [i[0] if isinstance(i, (list, tuple)) else i for i in indices]
            results_xyxy = results_xyxy[indices]
        else:
            results_xyxy = []

    return results_xyxy

def get_lettuce_mask(bgr_img, conf_threshold=0.25, iou_threshold=0.45, img_size=320):
    """
    Run YOLO on a BGR image and return:
      - lettuce_mask: uint8 (0/255) same size as bgr_img
      - boxes: list of [x1, y1, x2, y2, score, cls]
    """
    # preprocess
    blob, r, dw, dh, img_w, img_h = preprocess_frame(bgr_img, img_size)

    # run onnx model
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: blob})
    predictions = outputs[0]

    # postporcess
    boxes = postprocess(predictions, r, dw, dh, img_w, img_h,
                        conf_threshold=conf_threshold,
                        iou_threshold=iou_threshold)

    # lettuce mask
    lettuce_mask = np.zeros((img_h, img_w), dtype=np.uint8)
    for (x1, y1, x2, y2, score, cls) in boxes:
        # fill bbox area as lettuce = 255
        cv2.rectangle(
            lettuce_mask,
            (int(max(0, x1)), int(max(0, y1))),
            (int(min(img_w - 1, x2)), int(min(img_h - 1, y2))),
            255,
            thickness=-1
        )

    return lettuce_mask, boxes
