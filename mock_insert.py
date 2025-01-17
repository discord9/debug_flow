import time
import psycopg
from psycopg import sql
from live_connection import LiveConnectionLog

# 数据库连接配置
DB_CONFIG = {"dbname": "public", "host": "localhost", "port": 4003}

# SQL插入语句
INSERT_SQL = """
INSERT INTO live_connection_log (
    os, app_version, view_mode, first_frame_time, p2p_sdk_version,
    connect_retry_times, video_definition, net_mode, iot_online,
    entry_mode, device_model, device_mac, device_mac_suffix,
    device_firmware_version, connect_step, connect_result,
    connect_mode, connect_error, connect_id, connect_protocol,
    transport_protocol, isCamSDK, connect_step1_time,
    connect_step2_time, record_time
) VALUES (
%s, %s, %s, %s, %s,
%s, %s, %s, %s, %s,
%s, %s, %s, %s, %s,
%s, %s, %s, %s, %s,
%s, %s, %s, %s, %s);
"""


def generate_data_batch():
    """生成一批数据，1000条时间线，每条5行"""
    data = []
    combinations = LiveConnectionLog.generate_device_combinations(1000)

    for model, mac_suffix in combinations:
        mock_data = LiveConnectionLog.generate_mock_data(
            device_model=model, device_mac_suffix=mac_suffix, num_rows=5
        )
        data.extend([log.to_tuple() for log in mock_data])

    return data


def insert_data(cursor, data: list[tuple]):
    """将数据批量插入数据库"""
    for row in data:
        cursor.execute(INSERT_SQL, row)

    try:
        print(f"成功插入 {len(data)} 条数据")
    except Exception as e:
        print(f"插入数据时出错: {e}")
        print(f"SQL 语句: {INSERT_SQL}")
        print(f"第一条数据示例: {data[0] if data else '无数据'}")
        print(f"错误详情: {str(e)}")


def create_table_flow():
    with open("prod-camera-connection.sql", "r") as f:
        sql = f.read()
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()


def main():
    create_table_flow()

    # 创建数据库连接
    conn = psycopg.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()

        while True:
            start_time = time.time()

            # 生成数据
            data = generate_data_batch()

            # 插入数据库
            insert_data(cur, data)
            conn.commit()

            # 计算并等待剩余时间
            elapsed = time.time() - start_time
            if elapsed < 1:
                time.sleep(1 - elapsed)
    finally:
        # 确保连接关闭
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
