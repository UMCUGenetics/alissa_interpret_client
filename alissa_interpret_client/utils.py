def snake_to_camel_case(snake_str):
    """
    Convert a snake style formatted string to camel case.

    :param snake_str: Sanke style formatted string n

    """
    items = snake_str.split('_')
    return '{0}{1}'.format(items[0], ''.join(item.title() for item in items[1:]))


def kwargs_to_dict(**kwargs):
    """Convert keyword arguments to a dictionary."""
    dictionary = dict()
    for key, value in kwargs.items():
        if value:
            dictionary[snake_to_camel_case(key)] = value
    return dictionary
