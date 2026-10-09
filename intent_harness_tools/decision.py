"""The tolerance decision."""


def decide(quantity, tolerance):
    """'Yes' when |quantity| is inside the tolerance, else 'No'."""
    if abs(quantity) <= tolerance:
        return "Yes"
    return "No"
