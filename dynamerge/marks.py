class ScopeParser:
    """TODO provide map-based declaration of marks"""

    @staticmethod
    def parse_container(container: dict | list):
        """
        Parse dynaconf_marks from within container (dict or list).
        Return list of (mark_attr, new_value) tuples.
        """
        mark_list = []
        if isinstance(container, dict):
            mark_list += ScopeParser.parse_from_dict(container)
        elif isinstance(container, list):
            mark_list += ScopeParser.parse_from_list(container)
        return mark_list

    @staticmethod
    def parse_from_dict(dict_data: dict) -> list:
        """
        Parse and pop/mutates (when applicable) dynaconf marks from a dict and
        return list of (mark_attr, new_value) tuples.
        """
        mark_list = []
        merge = dict_data.pop("dynaconf_merge", None)
        merge_unique = dict_data.pop("dynaconf_merge_unique", None)
        if merge is not None:
            mark_list.append(("merge", merge))
        if merge_unique is not None:
            mark_list.append(("merge_unique", merge_unique))

        return mark_list

    @staticmethod
    def parse_from_list(list_data: list) -> list:
        """
        Parse and pop/mutates (when applicable) dynaconf marks from a list and
        return list of (mark_attr, new_value) tuples.
        """
        mark_list = []
        # reverse loop
        for i in range(len(list_data) - 1, 0, -1):
            if not isinstance(list_data[i], str):
                continue

            value = list_data[i].lower()
            if value in ("dynaconf_merge",):
                list_data.pop(i)
                mark_list.append(("merge", True))
            elif value in ("dynaconf_merge=false",):
                list_data.pop(i)
                mark_list.append(("merge", False))
            elif value in ("dynaconf_merge_unique",):
                list_data.pop(i)
                mark_list.append(("merge_unique", True))
            elif value.startswith("dynaconf_id_key="):
                list_data.pop(i)
                mark_list.append(("dict_id_key", value[value.find("=") + 1 :]))
            elif value in ("@empty"):
                list_data[i] = None
        return mark_list

    @staticmethod
    def pop_from_dict(dict_data: dict):
        ...
