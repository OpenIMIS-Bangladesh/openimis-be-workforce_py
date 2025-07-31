def clean_dependents_data(dependents_data):
    """
    Filters out completely empty items from dependents_data.

    Considered invalid (and removed):
        - Empty dicts: [{}]
        - Non-dict types like [{""}], [{" "}]

    Considered valid (and kept):
        - Dicts with at least one key, even if value is empty (e.g., [{"name": ""}])

    :param dependents_data: list of dependent objects
    :return: cleaned list, or empty list if nothing valid
    """
    if not isinstance(dependents_data, list):
        return []

    def is_valid_dependent(dep):
        return isinstance(dep, dict) and bool(dep.keys())

    return [dep for dep in dependents_data if is_valid_dependent(dep)]
