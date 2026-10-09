from tests.fakes import AddTwiceIntent, EchoIntent


def register(harness, **options):
    harness.register_intent(EchoIntent())
    harness.register_intent(AddTwiceIntent())
