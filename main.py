import argparse
import json
from collections import defaultdict
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Анализ лог-файлов"
    )
    parser.add_argument(
        "--file",
        nargs='+',
        required=True,
        help="Путь к файлу"
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Название отчета"
    )
    parser.add_argument(
        "--date",
        help="Отчеты с указанной даты YYYY-MM-DD"
    )
    args = parser.parse_args()
    run_report(args)


def run_report(args):
    response_data = defaultdict(lambda: {
        "total_response_time": 0.0,
        "count": 0
    })
    today = datetime.today().date()
    if args.date:
        try:
            date_arg = datetime.strptime(
                args.date,
                "%Y-%m-%d"
            ).date()
            if date_arg > today:
                raise ValueError(
                    f"Указанная дата ({date_arg}) "
                    f"находится в будущем!"
                )
        except ValueError:
            raise ValueError(
                "Неверный формат даты: "
                "используйте YYYY-MM-DD"
            )
    for file in args.file:
        try:
            with open(file, "r") as f:
                for line in f:
                    try:
                        log = json.loads(line)
                    except json.JSONDecodeError as e:
                        raise ValueError(
                            "Ошибка чтения JSON в строке: "
                            f"{line.strip()}"
                        ) from e
                    if not isinstance(log, dict):
                        raise TypeError(
                            f"⚠️ JSON не является объектом "
                            f"(dict): {line.strip()}"
                        )
                    if args.date:
                        date = log.get("@timestamp")
                        if not date:
                            continue
                        try:
                            date_log = datetime.strptime(
                                date[:10],
                                "%Y-%m-%d"
                            ).date()
                        except ValueError:
                            print(
                                f"⚠️ Неверный формат даты: {date} "
                                f"в строке: {line.strip()}"
                            )
                            continue
                        if date_log < date_arg:
                            continue
                    url = log.get("url")
                    rt = log.get("response_time")
                    if url is not None and isinstance(rt, (int, float)):
                        rt = float(rt)
                        if rt < 0:
                            raise ValueError(
                                "Время ответа не может быть "
                                "меньше или равно 0"
                            )
                        response_data[url]["total_response_time"] += rt
                        response_data[url]["count"] += 1
                    else:
                        print(
                            f"⚠️ Пропущены некорректные данные: "
                            f"{line.strip()}"
                        )
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при открытии файла {file}: {e}")
    if not response_data:
        print(
            "⚠️ Нет данных для отчета — "
            "файл пуст, либо содержит некорректные данные!"
        )
        return None
    with open(args.report, "w") as report_file:
        header = f"{'№':<4} {'URL':<30} {'Average':>10} {'Amount':>10}"
        separator = "-" * len(header)
        print(header)
        print(separator)
        report_file.write(header + "\n")
        report_file.write(separator + "\n")
        for i, (url, data) in enumerate(response_data.items(), start=1):
            avg = (
                data["total_response_time"] /
                data["count"] if
                data["count"] >
                0 else 0
            )
            count = data["count"]
            line = f"{i:<4} {url:<30} {avg:>10.2f} {count:>10}"
            print(line)
            report_file.write(line + "\n")


if __name__ == "__main__":
    main()
