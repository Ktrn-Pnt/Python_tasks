import sys

CLIENT_INDEX = 0
RESOURCE_INDEX = 13


def read_params():
    argv = sys.argv
    return argv


def read_data_file():
    file_name = read_params()[1]
    lines = []
    with open(file_name, errors="ignore") as f:
        lines.extend(f.readline() for i in range(20))

    return lines


def get_active_client():
    active_client = get_most_repeated_object(CLIENT_INDEX)
    result = "\n".join(active_client)
    return f"MostActiveClient:\n{result}"


def get_popular_resource():
    popular_resource = get_most_repeated_object(RESOURCE_INDEX)
    result = "\n".join(popular_resource)
    return f"MostPopularPage:\n{result}"


def get_most_repeated_object(index: int):
    stat = {}
    lines = read_data_file()
    for line in lines:
        line_segments = line.split(",")
        stat_object = line_segments[index]
        if stat_object not in stat:
            stat[stat_object] = 0
        stat[stat_object] += 1

    max_value = max(stat.values())
    most_repeated_object = {k: v for k, v in stat.items() if v == max_value}
    return list(most_repeated_object.keys())


def get_client_stat():
    return get_stat(CLIENT_INDEX)


def get_resource_stat():
    return get_stat(RESOURCE_INDEX)


def get_stat(index: int):
    stat = {}
    lines = read_data_file()
    for line in lines:
        line_segments = line.split(",")
        stat_object = line_segments[index]
        if stat_object not in stat:
            stat[stat_object] = 0
        stat[stat_object] += 1

    return create_sorted_top(stat)


def create_sorted_top(stats: dict[str, int]) -> str:
    result = []
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    sorted_top = dict(sorted_stats)
    for key in sorted_top:
        result.append(f"{key}: {sorted_top[key]}")

    return "\n".join(result)


def print_stat():
    stat_object = read_params()[2]
    if stat_object == "c":
        print(get_client_stat())
    if stat_object == "r":
        print(get_resource_stat())
    if stat_object == "ac":
        print(get_active_client())
    if stat_object == "pr":
        print(get_popular_resource())


if __name__ == '__main__':
    print_stat()
