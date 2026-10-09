"""SAM 3 concept segmentation and the region helpers used to count parts.

Plain functions. A region is a dict:

    box    [x1, y1, x2, y2] as fractions of the image width and height
    score  the model's score for the region, 0 to 1
    mask   (H, W) bool array at full image size

`segment_concept` needs torch and transformers (the "models" extra). They are imported inside the
function, so importing this module does not load them. The model loads once, from the local
cache only.

The helpers copy the rules of the experiment (grounded-count-harness, notebooks 07 and 08):

- `keep_smaller_regions`: keep a region only when its box is smaller than a fraction of a
  reference box (the animal), then keep the highest scores, at most a limit.
- `remove_duplicate_regions`: go down the regions by score; stop at the threshold; drop a region
  that overlaps a kept region with IoU of at least 0.5, or (nested rule) lies at least 0.7 inside
  a kept region. Masks are compared at 128 px on the long side.
"""

import numpy as np
from PIL import Image

SAM3_MODEL_ID = "facebook/sam3"
MIN_SCORE = 0.01          # every region with at least this score is returned
MASK_THRESHOLD = 0.5      # mask logits to a boolean mask
MASK_SIDE = 128           # masks are compared at this size on the long side
IOU_LIMIT = 0.5           # two regions with at least this IoU are one region
CONTAINMENT_LIMIT = 0.7   # nested rule: a region at least this share inside another is a duplicate

_loaded = {}              # model id -> (processor, model, device)


def pick_device():
    """MPS when it is there, then CUDA, then CPU."""
    import torch

    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _sam3(model_id):
    if model_id not in _loaded:
        from transformers import Sam3Model, Sam3Processor

        device = pick_device()
        processor = Sam3Processor.from_pretrained(model_id, local_files_only=True)
        model = Sam3Model.from_pretrained(model_id, local_files_only=True).to(device).eval()
        _loaded[model_id] = (processor, model, device)
    return _loaded[model_id]


def mask_to_box(mask):
    """The box around the True pixels as image fractions, or None for an empty mask."""
    rows, cols = np.where(mask)
    if len(cols) == 0:
        return None
    height, width = mask.shape
    return [cols.min() / width, rows.min() / height, (cols.max() + 1) / width, (rows.max() + 1) / height]


def small_mask(mask, side=MASK_SIDE):
    """The same mask with `side` pixels on its long side (nearest neighbour)."""
    height, width = mask.shape
    scale = side / max(height, width)
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return np.array(Image.fromarray(mask).resize(size, Image.NEAREST))


def segment_concept(image, concept, min_score=MIN_SCORE, model_id=SAM3_MODEL_ID):
    """Every region of `concept` that SAM 3 finds in `image`, with a score of at least `min_score`.

    Regions with an empty mask are dropped. The order is the model's order.
    """
    import torch

    processor, model, device = _sam3(model_id)
    image = image.convert("RGB")
    inputs = processor(images=image, text=concept, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    width, height = image.size
    result = processor.post_process_instance_segmentation(
        outputs, threshold=min_score, mask_threshold=MASK_THRESHOLD, target_sizes=[(height, width)]
    )[0]
    masks = result["masks"].cpu().numpy().astype(bool)          # (n, H, W)
    scores = result["scores"].float().cpu().numpy()              # (n,)
    regions = []
    for mask, score in zip(masks, scores):
        box = mask_to_box(mask)
        if box is not None:
            regions.append({"box": box, "score": float(score), "mask": mask})
    return regions


def box_area(box):
    """Area of an [x1, y1, x2, y2] box in image fractions."""
    return (box[2] - box[0]) * (box[3] - box[1])


def keep_smaller_regions(regions, reference_box, fraction=0.5, max_regions=150):
    """Regions whose box is smaller than `fraction` of the reference box, highest scores first,
    at most `max_regions`."""
    limit = fraction * box_area(reference_box)
    small = []
    for region in regions:
        if box_area(region["box"]) < limit:
            small.append(region)
    small.sort(key=lambda region: region["score"], reverse=True)
    return small[:max_regions]


def remove_duplicate_regions(regions, threshold, nested=True,
                             iou_limit=IOU_LIMIT, containment_limit=CONTAINMENT_LIMIT,
                             mask_side=MASK_SIDE):
    """The regions that count: at or above `threshold`, each one distinct from a region with a
    higher score.

    `regions` must be sorted by score, highest first (as `keep_smaller_regions` returns them).
    The walk stops at the first region below the threshold.
    """
    kept = []
    kept_flat = []
    for region in regions:
        if region["score"] < threshold:
            break
        flat = small_mask(region["mask"], mask_side).reshape(-1).astype(np.float32)   # (pixels,)
        own = float(flat.sum())
        duplicate = False
        for other in kept_flat:
            inter = float(flat @ other)
            union = own + float(other.sum()) - inter
            if union > 0 and inter / union >= iou_limit:
                duplicate = True
                break
            if nested and own > 0 and inter / own >= containment_limit:
                duplicate = True
                break
        if not duplicate:
            kept.append(region)
            kept_flat.append(flat)
    return kept
