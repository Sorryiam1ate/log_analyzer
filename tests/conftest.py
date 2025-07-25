import tempfile


def create_temp_log(lines: list[str] or str):
    if isinstance(lines, str):
        lines = [lines]
    with tempfile.NamedTemporaryFile(
        mode="w+",
        delete=False
    ) as temp_log:
        for line in lines:
            temp_log.write(line)
        return temp_log.name


def create_temp_report():
    with tempfile.NamedTemporaryFile(
        mode="w+",
        delete=False
    ) as temp_report:
        return temp_report.name
