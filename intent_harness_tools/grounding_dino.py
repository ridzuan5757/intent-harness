"""The box of one object from GroundingDINO, as image fractions.

A plain function. It needs torch and transformers (the "models" extra). They are imported inside
the function, so importing this module does not load them. The model loads once, from the local
cache only.

The leg pipeline uses it for the animal box: the experiment kept a leg region only when its box
was smaller than half the animal box (grounded-count-harness, notebooks 07 and 08).
"""

DINO_MODEL_ID = "IDEA-Research/grounding-dino-tiny"
MIN_SCORE = 0.01

_loaded = {}              # model id -> (processor, model, device)


def _dino(model_id):
    if model_id not in _loaded:
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

        from intent_harness_tools.sam3 import pick_device

        device = pick_device()
        processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(
            model_id, local_files_only=True
        ).to(device).eval()
        _loaded[model_id] = (processor, model, device)
    return _loaded[model_id]


def _clip01(value):
    return min(1.0, max(0.0, value))


def best_box(image, query, min_score=MIN_SCORE, model_id=DINO_MODEL_ID):
    """The box with the highest score for `query`, as [x1, y1, x2, y2] image fractions.

    When no box has a score of at least `min_score`, the box is the whole image.
    """
    import torch

    processor, model, device = _dino(model_id)
    image = image.convert("RGB")
    inputs = processor(images=image, text=query.lower() + ".", return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    width, height = image.size
    result = processor.post_process_grounded_object_detection(
        outputs, inputs["input_ids"], threshold=min_score, text_threshold=0.0,
        target_sizes=[(height, width)],
    )[0]
    best = None
    for box, score in zip(result["boxes"].float().cpu().numpy(), result["scores"].float().cpu().numpy()):
        x1, y1 = _clip01(float(box[0]) / width), _clip01(float(box[1]) / height)
        x2, y2 = _clip01(float(box[2]) / width), _clip01(float(box[3]) / height)
        if x2 > x1 and y2 > y1 and (best is None or float(score) > best[1]):
            best = ([x1, y1, x2, y2], float(score))
    if best is None:
        return [0.0, 0.0, 1.0, 1.0]
    return best[0]
