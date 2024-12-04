import logging
import re
import sqlite3
from argparse import ArgumentParser
from datetime import datetime, timezone
from typing import NamedTuple
from zoneinfo import ZoneInfo
from pathlib import Path

from pydantic import TypeAdapter

JST = ZoneInfo(key="Asia/Tokyo")
logger = logging.getLogger(__name__)

class HistoryItem(NamedTuple):
    urls_url: str
    urls_title: str
    visits_visit_time: int


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--database_file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--year_month",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="work",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    database_file: str = args.database_file
    year_month: str = args.year_month
    output_dir_string: str = args.output_dir

    output_dir = Path(output_dir_string)

    year_month_match = re.match(r"^(\d+)-(\d+)$", year_month)
    if not year_month_match:
        raise Exception("year_month is not Y-m format")

    year = int(year_month_match.group(1))
    month = int(year_month_match.group(2))

    first_day_of_month = datetime(
        year=year,
        month=month,
        day=1,
        tzinfo=JST,
    )

    next_month_year = year + month // 12
    next_month = month % 12 + 1

    first_day_of_next_month = datetime(
        year=next_month_year,
        month=next_month,
        day=1,
        tzinfo=JST,
    )

    logger.info(f"Start time: {first_day_of_month.isoformat()}")
    logger.info(f"End time: {first_day_of_next_month.isoformat()}")

    chrome_zero_datetime = datetime(1601, 1, 1, tzinfo=timezone.utc)

    start_visit_time = int(
        (first_day_of_month.timestamp() - chrome_zero_datetime.timestamp()) * 10**6
    )
    end_visit_time = int(
        (first_day_of_next_month.timestamp() - chrome_zero_datetime.timestamp()) * 10**6
    )

    items: list[HistoryItem] = []

    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
SELECT urls.url, urls.title, visits.visit_time
FROM visits
JOIN urls ON visits.url = urls.id
WHERE visits.visit_time >= :start_visit_time
AND visits.visit_time < :end_visit_time
ORDER BY visits.visit_time
""",
            {
                "start_visit_time": start_visit_time,
                "end_visit_time": end_visit_time,
            },
        )

        for row in cursor:
            item = TypeAdapter(HistoryItem).validate_python(row)
            items.append(item)

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"chrome_history_{year:04d}-{month:02d}.tsv"
    with output_path.open(mode="w", encoding="utf-8") as fp:
        for item in items:
            visit_datetime = datetime.fromtimestamp(
                item.visits_visit_time / 10**6 + chrome_zero_datetime.timestamp(),
                tz=JST,
            )

            fp.write(
                "\t".join(
                    [
                        visit_datetime.isoformat(),
                        item.urls_title,
                        item.urls_url,
                    ]
                )
                + "\n"
            )


if __name__ == "__main__":
    main()
