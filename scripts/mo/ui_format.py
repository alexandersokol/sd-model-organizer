def format_percentage(part, total):
    return int((part / total) * 100)


def format_bytes(bytes_to_format):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while bytes_to_format >= 1000 and i < len(units) - 1:
        bytes_to_format /= 1000
        i += 1
    return f"{bytes_to_format:.2f} {units[i]}"


def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    else:
        return f"{int(m):02d}:{int(s):02d}"


def format_download_speed(speed):
    if speed is None:
        return 'Undefined'

    units = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']
    unit_index = 0

    while speed >= 1000 and unit_index < len(units) - 1:
        speed /= 1000.0
        unit_index += 1

    return '{:.2f}{}'.format(speed, units[unit_index])


def format_exception(ex):
    return f"{type(ex).__name__}: {str(ex)}".replace('"', '\\"').replace("'", "\\'")
