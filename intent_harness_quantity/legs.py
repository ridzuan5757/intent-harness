"""The legs pipeline: count the legs of an animal with SAM 3, in code.

The steps and constants are those of the experiment (grounded-count-harness, notebooks 07 and
08), chosen on the 1,098 original images only:

1. best_box: the animal box from GroundingDINO tiny, query "animal".
2. segment_concept: every SAM 3 region of the concept "leg" with a score of at least 0.01.
3. keep_smaller_regions: keep regions whose box is smaller than half the animal box, the 150
   highest scores.
4. remove_duplicate_regions: threshold 0.48, nested merge (IoU 0.5, containment 0.7).
5. The count is the number of regions that remain.
"""

ANIMAL_QUERY = "animal"
CONCEPT = "leg"
MIN_SCORE = 0.01
SIZE_RULE = 0.5
MAX_REGIONS = 150
THRESHOLD = 0.48
NESTED = True


class LegsPipeline:
    """Counts animal legs from SAM 3 regions."""

    name = "legs"
    required_tools = ("best_box", "segment_concept", "keep_smaller_regions", "remove_duplicate_regions")

    def count(self, image, question, tools):
        animal = tools["best_box"](image, ANIMAL_QUERY)
        regions = tools["segment_concept"](image, CONCEPT, min_score=MIN_SCORE)
        regions = tools["keep_smaller_regions"](regions, animal, fraction=SIZE_RULE, max_regions=MAX_REGIONS)
        legs = tools["remove_duplicate_regions"](regions, THRESHOLD, nested=NESTED)
        return len(legs)
