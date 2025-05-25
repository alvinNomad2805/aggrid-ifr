def create_range_axis(data_source, field):
    max_value = max(data_source[field]) + (0.1 * max(data_source[field]))
    min_value = min(data_source[field]) + (0.1 * min(data_source[field]))
    range_limit = max(abs(max_value), abs(min_value))

    return range_limit