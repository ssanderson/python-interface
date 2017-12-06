"""String formatting utilities.
"""


def bulleted_list(items):
    return "\n".join(map("  - {}".format, items))
