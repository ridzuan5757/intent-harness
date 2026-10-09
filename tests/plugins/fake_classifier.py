from tests.fakes import FixedClassifier

RECEIVED = {}


def register(harness, **options):
    RECEIVED.clear()
    RECEIVED.update(options)
    harness.register_classifier(FixedClassifier("sum"))
