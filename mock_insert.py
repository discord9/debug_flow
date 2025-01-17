import time
import subprocess
import psycopg
from live_connection import LiveConnectionLog
import datetime

# 数据库连接配置
DB_CONFIG = {"dbname": "public", "host": "localhost", "port": 4003, "autocommit": True}

# SQL插入语句
INSERT_SQL = """INSERT INTO live_connection_log (
    os, app_version, view_mode, first_frame_time, p2p_sdk_version,
    connect_retry_times, video_definition, net_mode, iot_online,
    entry_mode, device_model, device_mac, device_mac_suffix,
    device_firmware_version, connect_step, connect_result,
    connect_mode, connect_error, connect_id, connect_protocol,
    transport_protocol, isCamSDK, connect_step1_time,
    connect_step2_time, record_time
) VALUES {};
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
    try:
        # 将数据格式化为psql可接受的格式
        values = []
        for row in data:
            # 将每个值转换为字符串并转义单引号
            formatted_row = []
            for value in row:
                if value is None:
                    formatted_row.append("NULL")
                elif isinstance(value, str):
                    formatted_row.append(repr(value))
                else:
                    formatted_row.append(str(value))
            values.append(f"({', '.join(formatted_row)})")
        # make a tmp file to store the data
        with open("tmp.sql", "w") as f:
            # 构建完整的INSERT语句
            insert_cmd = INSERT_SQL.format(", ".join(values))
            f.write(insert_cmd)

        # 使用psql命令执行插入
        psql_cmd = f"psql -h {DB_CONFIG['host']} -p {DB_CONFIG['port']} -d {DB_CONFIG['dbname']} -f tmp.sql"
        subprocess.run(psql_cmd, shell=True, check=True)

        print(f"成功插入 {len(data)} 条数据， 时间：{datetime.datetime.now().isoformat()}")
    except Exception as e:
        print(f"插入数据时出错: {e}")
        print(f"第一条数据示例: {data[0] if data else '无数据'}")
        print(f"错误详情: {str(e)}")


def create_table_flow():
    psql_cmd = f"psql -h {DB_CONFIG['host']} -p {DB_CONFIG['port']} -d {DB_CONFIG['dbname']} -f prod-camera-connection.sql"
    subprocess.run(psql_cmd, shell=True, check=True)


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
            else:
                print("WARN: 数据生成和插入时间超过1秒")
    finally:
        # 确保连接关闭
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
