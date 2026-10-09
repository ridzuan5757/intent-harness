from tests.fakes import add


def register(harness, **options):
    harness.register_tool(add, name="add")
