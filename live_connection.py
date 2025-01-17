from datetime import datetime, timedelta
from typing import Optional, List
import random
import string

class LiveConnectionLog:
    def __init__(self):
        self.os: Optional[str] = None
        self.app_version: Optional[str] = None
        self.view_mode: Optional[str] = None
        self.first_frame_time: Optional[float] = None
        self.p2p_sdk_version: Optional[str] = None
        self.connect_retry_times: Optional[int] = None
        self.video_definition: Optional[int] = None
        self.net_mode: Optional[int] = None
        self.iot_online: Optional[int] = None
        self.entry_mode: Optional[int] = None
        self.device_model: Optional[str] = None
        self.device_mac: Optional[str] = None
        self.device_mac_suffix: Optional[str] = None
        self.device_firmware_version: Optional[str] = None
        self.connect_step: Optional[str] = None
        self.connect_result: Optional[int] = None
        self.connect_mode: Optional[str] = None
        self.connect_error: Optional[str] = None
        self.connect_id: Optional[str] = None
        self.connect_protocol: Optional[int] = None
        self.transport_protocol: Optional[str] = None
        self.isCamSDK: Optional[int] = None
        self.connect_step1_time: Optional[float] = None
        self.connect_step2_time: Optional[float] = None
        self.record_time: Optional[datetime] = None

    def __repr__(self):
        return f"LiveConnectionLog(device_model={self.device_model}, device_mac_suffix={self.device_mac_suffix})"

    def to_tuple(self) -> tuple:
        fields = [
            self.os,
            self.app_version,
            self.view_mode,
            self.first_frame_time,
            self.p2p_sdk_version,
            self.connect_retry_times,
            self.video_definition,
            self.net_mode,
            self.iot_online,
            self.entry_mode,
            self.device_model,
            self.device_mac,
            self.device_mac_suffix,
            self.device_firmware_version,
            self.connect_step,
            self.connect_result,
            self.connect_mode,
            self.connect_error,
            self.connect_id,
            self.connect_protocol,
            self.transport_protocol,
            self.isCamSDK,
            self.connect_step1_time,
            self.connect_step2_time,
            self.record_time.isoformat() if self.record_time else None
        ]
        return tuple(fields)

    def to_csv(self) -> str:
        """将对象字段按顺序输出为逗号分隔的字符串
        
        Returns:
            逗号分隔的字段值字符串
        """
        fields = self.to_tuple()
        return ",".join(str(field) if field is not None else "" for field in fields)

    @staticmethod
    def generate_device_combinations(num_combinations: int) -> List[to_tuple]:
        """生成指定数量的不重复的device_model和device_mac_suffix组合
        
        Args:
            num_combinations: 需要生成的组合数量
            
        Returns:
            包含(device_model, device_mac_suffix)元组的列表
        """
        combinations = set()
        
        while len(combinations) < num_combinations:
            model = f"MODEL-{random.randint(1000, 9999)}"
            mac_suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
            combinations.add((model, mac_suffix))
            
        return list(combinations)

    @staticmethod
    def generate_mock_data(
        device_model: str,
        device_mac_suffix: str,
        num_rows: int,
        seed: int = 42
    ) -> List["LiveConnectionLog"]:
        """生成模拟数据
        
        Args:
            device_model: 设备型号
            device_mac_suffix: 设备MAC地址后缀
            num_rows: 生成的行数
            seed: 随机数种子
            
        Returns:
            包含模拟数据的LiveConnectionLog对象列表
        """
        random.seed(seed)
        results = []
        
        for i in range(num_rows):
            log = LiveConnectionLog()
            log.device_model = device_model
            log.device_mac_suffix = device_mac_suffix
            log.os = random.choice(["iOS", "Android"])
            log.app_version = f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            log.view_mode = random.choice(["landscape", "portrait"])
            log.first_frame_time = random.uniform(0.5, 5.0)
            log.p2p_sdk_version = f"{random.randint(1, 3)}.{random.randint(0, 9)}"
            log.connect_retry_times = random.randint(0, 3)
            log.video_definition = random.choice([720, 1080, 1440, 2160])
            log.net_mode = random.randint(0, 3)
            log.iot_online = random.randint(0, 1)
            log.entry_mode = random.randint(0, 2)
            log.device_mac = f"00:11:22:33:44:{device_mac_suffix}"
            log.device_firmware_version = f"{random.randint(1, 5)}.{random.randint(0, 9)}"
            log.connect_step = random.choice(["init", "handshake", "streaming"])
            log.connect_result = random.randint(0, 1)
            log.connect_mode = random.choice(["P2P", "Relay"])
            log.connect_error = random.choice(["", "timeout", "network error"])
            log.connect_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            log.connect_protocol = random.randint(0, 2)
            log.transport_protocol = random.choice(["TCP", "UDP"])
            log.isCamSDK = random.randint(0, 1)
            log.connect_step1_time = random.uniform(0.1, 1.0)
            log.connect_step2_time = random.uniform(0.1, 1.0)
            log.record_time = datetime.now() - timedelta(minutes=random.randint(0, 1440))
            
            results.append(log)
            
        return results

if __name__ == "__main__":
    # 根据10条时间线各生成两行模拟数据

    pks = LiveConnectionLog.generate_device_combinations(10)
    mock_data = []
    for pk in pks:
        mock_data.extend(LiveConnectionLog.generate_mock_data(pk[0], pk[1], 2))

    # 打印生成的模拟数据
    for data in mock_data:
        print(data.to_csv())
