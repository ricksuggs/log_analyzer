import sqlite3
from datetime import datetime, timedelta
from app.config import config

conn_container = {}


def connect_db(connection_string):
    conn_container["conn"] = sqlite3.connect(connection_string)
    conn_container["conn"].row_factory = sqlite3.Row


def get_connection():
    if "conn" in conn_container:
        return conn_container["conn"]
    else:
        connect_db(config["sql_connection_string"])
        return conn_container["conn"]


def setup_database():
    conn = get_connection()
    with conn:
        conn.execute(
            """
            create table if not exists log_entries (
                id integer primary key,
                ip varchar,
                user varchar,
                date datetime,
                method varchar,
                request_path varchar,
                section varchar,
                http_version varchar,
                status_code varchar,
                response_size varchar,
                referrer varchar,
                user_agent varchar
            );
        """
        )
        conn.execute(
            """
            create index if not exists log_entries_date_idx on log_entries (date);
        """
        )
        conn.execute(
            """
            create index if not exists log_entries_section_idx on log_entries (section);
        """
        )
        conn.execute(
            """
            create table if not exists alerts (
                id integer primary key,
                create_datetime datetime,
                hits numeric,
                recovered int default 0
            );
        """
        )


def close_connection():
    conn = get_connection()
    conn.close()


def insert_log_entries(log_entries):
    conn = get_connection()
    with conn:
        conn.executemany(
            """
            insert into log_entries (
                ip,
                user,
                date,
                method,
                request_path,
                section,
                http_version,
                status_code,
                response_size,
                referrer,
                user_agent
            ) VALUES (
                :ip,
                :user,
                :date,
                :method,
                :request_path,
                :section,
                :http_version,
                :status_code,
                :response_size,
                :referrer,
                :user_agent
            )
        """,
            log_entries,
        )


def find_top_sections(from_datetime: datetime, to_datetime: datetime):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        select section, count(id) as section_count
        from log_entries
        where date >= :from_datetime and date <= :to_datetime 
        group by section
        order by count(id) desc
        limit 10
        """,
        {"from_datetime": from_datetime, "to_datetime": to_datetime},
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def create_alerts(to_datetime: datetime, seconds_back: int, threshold_average_rps: int):
    conn = get_connection()
    from_datetime = to_datetime - timedelta(
        seconds=seconds_back
    )  # type: datetime.datetime
    cur = conn.cursor()  # type: sqlite3.Cursor
    cur.execute(
        """
        select avg(entry_count) as entry_count_avg
        from (
            select 
                second as second,
                sum(entry_count) as entry_count
            from (
                with recursive seconds(second, entry_count) as (
                    select cast(strftime('%s', :from_datetime) as int) as second,
                    0 as entry_count
                    union all
                    select 
                        second+1 as second,
                        0 as entry_count
                        from seconds
                    where second < cast(strftime('%s', :to_datetime) as int)
                )
                select * from seconds
                union all
                select 
                    cast(strftime('%s', date) as int) as second, 
                    count(id) as entry_count
                from log_entries
                where date >= :from_datetime and date <= :to_datetime
                group by cast(strftime('%s', date) as int)
            )
            group by second
        );
        """,
        {"from_datetime": from_datetime, "to_datetime": to_datetime},
    )
    result = cur.fetchone()
    entry_count_avg = result["entry_count_avg"]
    if entry_count_avg > threshold_average_rps:
        cur.execute(
            """
            insert into alerts
            (
                create_datetime,
                hits
            )
            VALUES (
                :to_datetime,
                :hits
                )
            """,
            {"to_datetime": to_datetime, "hits": entry_count_avg},
        )
    else:
        # if the most recent alert is unresolved
        # get the most recent and set resolved to true
        cur.execute(
            """
            select * 
            from alerts 
            order by create_datetime desc
            limit 1
            """
        )
        result = cur.fetchone()
        if result and result["recovered"] == 0:
            cur.execute(
                """
            update alerts
            set recovered = 1
            where id = :id
            """,
                {"id": result["id"]},
            )

    conn.commit()
    cur.close()


def find_alerts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        select *
        from alerts
        order by create_datetime desc
        """
    )
    rv = cur.fetchall()
    cur.close()
    return rv


def purge_log_entries(to_datetime):
    conn = get_connection()
    with conn:
        conn.execute(
            """
            delete from log_entries
            where date <= :to_datetime
            """,
            {"to_datetime": to_datetime},
        )
        conn.commit()

