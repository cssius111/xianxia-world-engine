"""
技术和运营支持系统
- 存档管理
- 自动备份
- 错误处理
- 性能监控
"""

import gzip
import hashlib
import json
import os
import shutil
import threading
import time
import traceback

try:
    import psutil
except Exception:  # pragma: no cover - fallback when psutil not available

    class _DummyMem:
        def __init__(self) -> None:
            self.used = 0
            self.total = 0
            self.percent = 0

    class _DummyProcess:
        def memory_info(self) -> Any:
            class Info:
                rss = 0

            return Info()

        def cpu_percent(self) -> Any:
            return 0.0

    class psutil:  # type: ignore
        @staticmethod
        def cpu_percent(interval=None) -> Any:
            return 0.0

        @staticmethod
        def virtual_memory() -> Any:
            return _DummyMem()

        @staticmethod
        def Process():  # noqa: N802 - match psutil API
            return _DummyProcess()

        @staticmethod
        def cpu_count() -> Any:
            return 1


import base64
import logging
import pickle
import platform
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SaveGame:
    """存档数据"""

    save_id: str
    player_name: str
    save_time: float
    game_time: int
    version: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "save_id": self.save_id,
            "player_name": self.player_name,
            "save_time": self.save_time,
            "game_time": self.game_time,
            "version": self.version,
            "data": self.data,
            "metadata": self.metadata,
            "checksum": self.checksum,
        }


@dataclass
class ErrorLog:
    """错误日志"""

    error_id: str
    error_type: str
    error_msg: str
    traceback: str
    timestamp: float
    context: Dict[str, Any]
    severity: str  # low, medium, high, critical

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_msg": self.error_msg,
            "traceback": self.traceback,
            "timestamp": self.timestamp,
            "context": self.context,
            "severity": self.severity,
        }


class SaveManager:
    """存档管理器"""

    def __init__(self, save_dir: str = "saves") -> None:
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

        # 自动存档设置
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5分钟
        self.last_auto_save = 0
        self.max_saves_per_player = 10
        self.max_auto_saves = 3

        # 存档版本
        self.save_version = "1.0.0"

        # 备份设置
        self.backup_dir = self.save_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def create_save(
        self, player_name: str, game_state: Dict[str, Any], save_type: str = "manual"
    ) -> SaveGame:
        """创建存档"""
        # 生成存档ID
        save_id = self._generate_save_id(player_name, save_type)

        # 准备存档数据
        save_data = {
            "game_state": game_state,
            "save_type": save_type,
            "timestamp": time.time(),
        }

        # 计算校验和
        checksum = self._calculate_checksum(save_data)

        # 创建存档对象
        save_game = SaveGame(
            save_id=save_id,
            player_name=player_name,
            save_time=time.time(),
            game_time=game_state.get("game_time", 0),
            version=self.save_version,
            data=save_data,
            metadata={
                "save_type": save_type,
                "player_level": game_state.get("player", {}).get("level", 1),
                "location": game_state.get("current_location", "unknown"),
            },
            checksum=checksum,
        )

        # 保存到文件
        self._write_save_file(save_game)

        # 清理旧存档
        self._cleanup_old_saves(player_name, save_type)

        logger.info(f"创建存档: {save_id} (类型: {save_type})")
        return save_game

    def _generate_save_id(self, player_name: str, save_type: str) -> str:
        """生成存档ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{player_name}_{save_type}_{timestamp}"

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """计算校验和"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _write_save_file(self, save_game: SaveGame) -> None:
        """写入存档文件"""
        # 确定文件路径
        filename = f"{save_game.save_id}.save"
        filepath = self.save_dir / filename

        # 写入临时文件
        temp_filepath = filepath.with_suffix(".tmp")

        try:
            # 序列化数据
            save_dict = save_game.to_dict()

            # 压缩保存
            with gzip.open(temp_filepath, "wt", encoding="utf-8") as f:
                json.dump(save_dict, f, ensure_ascii=False, indent=2)

            # 原子性替换
            if filepath.exists():
                # 创建备份
                backup_path = self.backup_dir / f"{filename}.bak"
                shutil.copy2(filepath, backup_path)

            # 移动临时文件到最终位置
            temp_filepath.replace(filepath)

        except Exception as e:
            logger.error(f"保存存档失败: {e}")
            if temp_filepath.exists():
                temp_filepath.unlink()
            raise

    def load_save(self, save_id: str) -> Optional[SaveGame]:
        """加载存档"""
        filename = f"{save_id}.save"
        filepath = self.save_dir / filename

        if not filepath.exists():
            logger.error(f"存档不存在: {save_id}")
            return None

        try:
            # 读取压缩文件
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                save_dict = json.load(f)

            # 验证校验和
            data_copy = save_dict["data"].copy()
            stored_checksum = save_dict["checksum"]
            calculated_checksum = self._calculate_checksum(data_copy)

            if stored_checksum != calculated_checksum:
                logger.warning(f"存档校验和不匹配: {save_id}")
                # 可以选择是否继续加载

            # 创建存档对象
            save_game = SaveGame(
                save_id=save_dict["save_id"],
                player_name=save_dict["player_name"],
                save_time=save_dict["save_time"],
                game_time=save_dict["game_time"],
                version=save_dict["version"],
                data=save_dict["data"],
                metadata=save_dict.get("metadata", {}),
                checksum=save_dict["checksum"],
            )

            logger.info(f"加载存档成功: {save_id}")
            return save_game

        except Exception as e:
            logger.error(f"加载存档失败: {e}")
            return None

    def list_saves(self, player_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出存档"""
        saves = []

        for save_file in self.save_dir.glob("*.save"):
            try:
                # 快速读取元数据
                with gzip.open(save_file, "rt", encoding="utf-8") as f:
                    # 只读取必要的字段
                    save_data = json.load(f)

                    if player_name and save_data["player_name"] != player_name:
                        continue

                    saves.append(
                        {
                            "save_id": save_data["save_id"],
                            "player_name": save_data["player_name"],
                            "save_time": save_data["save_time"],
                            "game_time": save_data["game_time"],
                            "metadata": save_data.get("metadata", {}),
                            "file_size": save_file.stat().st_size,
                        }
                    )
            except Exception as e:
                logger.error(f"读取存档元数据失败: {save_file.name}: {e}")

        # 按时间排序
        saves.sort(key=lambda x: x["save_time"], reverse=True)
        return saves

    def delete_save(self, save_id: str) -> bool:
        """删除存档"""
        filename = f"{save_id}.save"
        filepath = self.save_dir / filename

        if filepath.exists():
            try:
                # 先备份
                backup_path = self.backup_dir / f"{filename}.deleted"
                shutil.move(str(filepath), str(backup_path))
                logger.info(f"删除存档: {save_id}")
                return True
            except Exception as e:
                logger.error(f"删除存档失败: {e}")

        return False

    def _cleanup_old_saves(self, player_name: str, save_type: str) -> None:
        """清理旧存档"""
        # 获取该玩家的所有存档
        player_saves = [
            s for s in self.list_saves(player_name) if s["metadata"].get("save_type") == save_type
        ]

        # 确定要保留的数量
        max_saves = self.max_auto_saves if save_type == "auto" else self.max_saves_per_player

        # 删除多余的存档
        if len(player_saves) > max_saves:
            saves_to_delete = player_saves[max_saves:]
            for save_info in saves_to_delete:
                self.delete_save(save_info["save_id"])

    def export_save(self, save_id: str, export_path: str) -> bool:
        """导出存档"""
        save_game = self.load_save(save_id)
        if not save_game:
            return False

        try:
            # 使用base64编码导出
            save_data = save_game.to_dict()
            encoded_data = base64.b64encode(json.dumps(save_data).encode("utf-8")).decode("utf-8")

            with open(export_path, "w") as f:
                f.write(f"XIANXIA_SAVE_V1\n{encoded_data}")

            logger.info(f"导出存档到: {export_path}")
            return True

        except Exception as e:
            logger.error(f"导出存档失败: {e}")
            return False

    def import_save(self, import_path: str) -> Optional[str]:
        """导入存档"""
        try:
            with open(import_path, "r") as f:
                lines = f.readlines()

            if not lines or not lines[0].strip().startswith("XIANXIA_SAVE"):
                logger.error("无效的存档文件格式")
                return None

            # 解码数据
            encoded_data = lines[1].strip()
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            save_dict = json.loads(decoded_data)

            # 创建存档对象
            save_game = SaveGame(
                save_id=save_dict["save_id"] + "_imported",
                player_name=save_dict["player_name"],
                save_time=time.time(),  # 使用当前时间
                game_time=save_dict["game_time"],
                version=save_dict["version"],
                data=save_dict["data"],
                metadata=save_dict.get("metadata", {}),
                checksum=save_dict["checksum"],
            )

            # 保存
            self._write_save_file(save_game)

            logger.info(f"导入存档成功: {save_game.save_id}")
            return save_game.save_id

        except Exception as e:
            logger.error(f"导入存档失败: {e}")
            return None


class ErrorHandler:
    """错误处理器"""

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 错误日志文件
        self.error_log_file = self.log_dir / "errors.log"
        self.crash_dir = self.log_dir / "crashes"
        self.crash_dir.mkdir(exist_ok=True)

        # 错误统计
        self.error_counts: Dict[str, int] = {}
        self.last_errors: List[ErrorLog] = []
        self.max_recent_errors = 100

        # 错误处理回调
        self.error_callbacks: List[Callable[[ErrorLog], Any]] = []

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "medium",
    ) -> str:
        """处理错误"""
        # 生成错误ID
        error_id = self._generate_error_id(error)

        # 获取详细信息
        error_type = type(error).__name__
        error_msg = str(error)
        tb = traceback.format_exc()

        # 创建错误日志
        error_log = ErrorLog(
            error_id=error_id,
            error_type=error_type,
            error_msg=error_msg,
            traceback=tb,
            timestamp=time.time(),
            context=context or {},
            severity=severity,
        )

        # 保存错误日志
        self._save_error_log(error_log)

        # 更新统计
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_errors.append(error_log)
        if len(self.last_errors) > self.max_recent_errors:
            self.last_errors.pop(0)

        # 触发回调
        for callback in self.error_callbacks:
            try:
                callback(error_log)
            except Exception as cb_error:
                logger.error(f"错误回调失败: {cb_error}")

        # 如果是严重错误，创建崩溃报告
        if severity == "critical":
            self._create_crash_report(error_log)

        logger.error(f"处理错误 [{severity}]: {error_type}: {error_msg}")
        return error_id

    def _generate_error_id(self, error: Exception) -> str:
        """生成错误ID"""
        error_str = f"{type(error).__name__}:{str(error)}:{time.time()}"
        return hashlib.md5(error_str.encode()).hexdigest()[:12]

    def _save_error_log(self, error_log: ErrorLog) -> None:
        """保存错误日志"""
        # 追加到日志文件
        with open(self.error_log_file, "a", encoding="utf-8") as f:
            log_line = json.dumps(error_log.to_dict(), ensure_ascii=False)
            f.write(log_line + "\n")

    def _create_crash_report(self, error_log: ErrorLog) -> None:
        """创建崩溃报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_file = self.crash_dir / f"crash_{timestamp}.txt"

        report = f"""# 崩溃报告

时间: {datetime.fromtimestamp(error_log.timestamp)}
错误ID: {error_log.error_id}
错误类型: {error_log.error_type}
错误信息: {error_log.error_msg}
严重程度: {error_log.severity}

## 调用栈
{error_log.traceback}

## 上下文
{json.dumps(error_log.context, ensure_ascii=False, indent=2)}

## 系统信息
- 平台: {platform.platform()}
- Python版本: {platform.python_version()}
- CPU使用率: {psutil.cpu_percent()}%
- 内存使用: {psutil.virtual_memory().percent}%
"""

        with open(crash_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.critical(f"创建崩溃报告: {crash_file}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": dict(self.error_counts),
            "recent_errors": [
                {
                    "time": datetime.fromtimestamp(e.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "type": e.error_type,
                    "msg": e.error_msg[:100],
                    "severity": e.severity,
                }
                for e in self.last_errors[-10:]
            ],
        }


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self) -> None:
        self.metrics: Dict[str, List[float]] = {
            "fps": [],
            "frame_time": [],
            "memory_usage": [],
            "cpu_usage": [],
        }

        self.monitoring = False
        self.monitor_thread = None
        self.sample_interval = 1.0  # 采样间隔（秒）

        # 性能阈值
        self.thresholds: Dict[str, float] = {
            "fps_min": 30,
            "memory_max_mb": 500,
            "cpu_max_percent": 80,
        }

        # 性能报警回调
        self.alert_callbacks: List[Callable[[Dict[str, Any]], Any]] = []

    def start_monitoring(self) -> None:
        """开始监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("性能监控已启动")

    def stop_monitoring(self) -> None:
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("性能监控已停止")

    def _monitor_loop(self) -> None:
        """监控循环"""
        while self.monitoring:
            try:
                # 收集指标
                metrics = self._collect_metrics()

                # 更新历史数据
                for key, value in metrics.items():
                    if key in self.metrics:
                        self.metrics[key].append(value)
                        # 保留最近1000个样本
                        if len(self.metrics[key]) > 1000:
                            self.metrics[key] = self.metrics[key][-1000:]

                # 检查阈值
                self._check_thresholds(metrics)

            except Exception as e:
                logger.error(f"性能监控错误: {e}")

            time.sleep(self.sample_interval)

    def _collect_metrics(self) -> Dict[str, float]:
        """收集性能指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # 内存使用
        memory = psutil.virtual_memory()
        memory_mb = memory.used / (1024 * 1024)

        # 进程特定信息
        try:
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024 * 1024)
            process_cpu = process.cpu_percent()
        except:
            process_memory = 0
            process_cpu = 0

        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory_mb,
            "process_memory": process_memory,
            "process_cpu": process_cpu,
            "timestamp": time.time(),
        }

    def _check_thresholds(self, metrics: Dict[str, float]) -> None:
        """检查阈值"""
        alerts = []

        # 检查内存使用
        if metrics.get("process_memory", 0) > self.thresholds["memory_max_mb"]:
            alerts.append(
                {
                    "type": "memory_high",
                    "value": metrics["process_memory"],
                    "threshold": self.thresholds["memory_max_mb"],
                }
            )

        # 检查CPU使用
        if metrics.get("process_cpu", 0) > self.thresholds["cpu_max_percent"]:
            alerts.append(
                {
                    "type": "cpu_high",
                    "value": metrics["process_cpu"],
                    "threshold": self.thresholds["cpu_max_percent"],
                }
            )

        # 触发报警
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"性能报警回调失败: {e}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        summary = {"current": {}, "average": {}, "peak": {}}

        # 当前值
        if self.metrics["cpu_usage"]:
            summary["current"]["cpu_usage"] = self.metrics["cpu_usage"][-1]
        if self.metrics["memory_usage"]:
            summary["current"]["memory_usage"] = self.metrics["memory_usage"][-1]

        # 平均值和峰值
        for metric_name, values in self.metrics.items():
            if values and isinstance(values[0], (int, float)):
                summary["average"][metric_name] = sum(values) / len(values)
                summary["peak"][metric_name] = max(values)

        return summary


class AutoBackupManager:
    """自动备份管理器"""

    def __init__(self, save_manager: SaveManager) -> None:
        self.save_manager = save_manager
        self.backup_enabled = True
        self.backup_interval = 3600  # 1小时
        self.last_backup_time = 0
        self.backup_thread = None
        self.running = False

    def start_auto_backup(self) -> None:
        """启动自动备份"""
        if self.running:
            return

        self.running = True
        self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.backup_thread.start()
        logger.info("自动备份已启动")

    def stop_auto_backup(self) -> None:
        """停止自动备份"""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=2)
        logger.info("自动备份已停止")

    def _backup_loop(self) -> None:
        """备份循环"""
        while self.running:
            current_time = time.time()

            if current_time - self.last_backup_time >= self.backup_interval:
                self._perform_backup()
                self.last_backup_time = current_time

            time.sleep(10)  # 每10秒检查一次

    def _perform_backup(self) -> None:
        """执行备份"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"

            # 创建备份目录
            backup_path = self.save_manager.backup_dir / backup_name
            if backup_path.exists():
                logger.warning(f"备份目录已存在，跳过本次备份: {backup_path}")
                return
            backup_path.mkdir()

            # 复制所有存档文件
            save_count = 0
            for save_file in self.save_manager.save_dir.glob("*.save"):
                if save_file.is_file():
                    shutil.copy2(save_file, backup_path)
                    save_count += 1

            # 创建备份信息文件
            backup_info = {
                "timestamp": time.time(),
                "save_count": save_count,
                "game_version": self.save_manager.save_version,
            }

            with open(backup_path / "backup_info.json", "w") as f:
                json.dump(backup_info, f, indent=2)

            logger.info(f"自动备份完成: {backup_name} (包含{save_count}个存档)")

            # 清理旧备份
            self._cleanup_old_backups()

        except Exception as e:
            logger.error(f"自动备份失败: {e}")

    def _cleanup_old_backups(self, max_backups: int = 10) -> None:
        """清理旧备份"""
        backups = []

        for backup_dir in self.save_manager.backup_dir.iterdir():
            if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
                info_file = backup_dir / "backup_info.json"
                if info_file.exists():
                    with open(info_file) as f:
                        info = json.load(f)
                        backups.append((backup_dir, info["timestamp"]))

        # 按时间排序
        backups.sort(key=lambda x: x[1], reverse=True)

        # 删除多余的备份
        for backup_dir, _ in backups[max_backups:]:
            shutil.rmtree(backup_dir)
            logger.info(f"删除旧备份: {backup_dir.name}")


class TechnicalOpsSystem:
    """技术运营系统"""

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            logger.debug("TechnicalOpsSystem 已初始化，跳过")
            return

        self._initialized = True

        self._last_backup_time: float = 0.0
        self._backup_interval: float = 30.0  # 最短30秒执行一次备份

        self.save_manager = SaveManager()
        self.error_handler = ErrorHandler()
        self.performance_monitor = PerformanceMonitor()
        self.backup_manager = AutoBackupManager(self.save_manager)

        # 启动自动功能
        self.performance_monitor.start_monitoring()
        self.backup_manager.start_auto_backup()

        # 崩溃保护
        self._setup_crash_protection()

    def _setup_crash_protection(self) -> None:
        """设置崩溃保护

        在非主线程环境（例如 WSGI 服务器中）注册信号处理会抛出 ``ValueError``，
        因此在此情况下仅注册 ``atexit`` 钩子并跳过信号处理。
        """
        import atexit
        import signal
        import threading

        # 注册退出处理
        atexit.register(self._on_exit)

        if threading.current_thread() is not threading.main_thread():
            logger.warning("Crash protection signal handlers skipped (not main thread)")
            return

        # 注册信号处理
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, "SIGINT"):
            signal.signal(signal.SIGINT, self._signal_handler)

    def _on_exit(self) -> None:
        """退出时的处理"""
        logger.info("游戏正在关闭...")

        # 停止监控
        self.performance_monitor.stop_monitoring()
        self.backup_manager.stop_auto_backup()

        # 保存性能报告
        self._save_performance_report()

    def _signal_handler(self, signum, frame) -> None:
        """信号处理"""
        logger.warning(f"收到信号: {signum}")
        # 可以在这里添加紧急保存等操作

    def _save_performance_report(self) -> None:
        """保存性能报告"""
        report = {
            "performance": self.performance_monitor.get_performance_summary(),
            "errors": self.error_handler.get_error_statistics(),
            "timestamp": time.time(),
        }

        report_file = self.error_handler.log_dir / "performance_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

    def try_backup(self) -> None:
        """在冷却时间内避免重复备份"""
        current = time.time()
        if current - self._last_backup_time < self._backup_interval:
            logger.info("跳过备份：距离上次备份时间过短")
            return

        self.backup_manager._perform_backup()
        self._last_backup_time = current

    def create_game_save(self, game_state: Dict[str, Any], save_type: str = "manual") -> str:
        """创建游戏存档"""
        player_name = game_state.get("player", {}).get("name", "unknown")
        save_game = self.save_manager.create_save(player_name, game_state, save_type)
        return save_game.save_id

    def load_game_save(self, save_id: str) -> Optional[Dict[str, Any]]:
        """加载游戏存档"""
        save_game = self.save_manager.load_save(save_id)
        if save_game:
            return save_game.data.get("game_state")
        return None

    def handle_game_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """处理游戏错误"""
        # 确定严重程度
        severity = "medium"
        if isinstance(error, (SystemError, MemoryError)):
            severity = "critical"
        elif isinstance(error, (KeyError, ValueError, TypeError)):
            severity = "high"

        # 处理错误
        error_id = self.error_handler.handle_error(error, context, severity)

        # 如果是严重错误，尝试自动保存
        if severity in ["critical", "high"] and context and "game_state" in context:
            try:
                self.create_game_save(context["game_state"], "crash")
                logger.info("崩溃存档已创建")
            except Exception as save_error:
                logger.error(f"创建崩溃存档失败: {save_error}")

        return error_id

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "performance": self.performance_monitor.get_performance_summary(),
            "errors": self.error_handler.get_error_statistics(),
            "saves": {
                "total": len(self.save_manager.list_saves()),
                "auto_save_enabled": self.save_manager.auto_save_enabled,
                "backup_enabled": self.backup_manager.backup_enabled,
            },
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            },
        }


# 全局实例
tech_ops_system = TechnicalOpsSystem()


def integrate_technical_features(game_core) -> None:
    """集成技术功能到游戏核心"""
    # 自动存档
    original_process_command = game_core.process_command
    command_count = 0

    def auto_save_wrapper(input_text: str) -> None:
        """带自动存档的命令处理"""
        nonlocal command_count
        command_count += 1

        # 每20个命令自动存档一次
        if command_count % 20 == 0 and game_core.game_state.player:
            try:
                save_id = tech_ops_system.create_game_save(game_core.game_state.to_dict(), "auto")
                logger.debug(f"自动存档: {save_id}")
            except Exception as e:
                logger.error(f"自动存档失败: {e}")

        # 错误保护
        try:
            original_process_command(input_text)
        except Exception as e:
            # 处理错误
            context = {
                "command": input_text,
                "game_state": (
                    game_core.game_state.to_dict()
                    if hasattr(game_core.game_state, "to_dict")
                    else {}
                ),
            }
            error_id = tech_ops_system.handle_game_error(e, context)

            # 显示友好的错误信息
            game_core.output(f"哎呀，出了点小问题 (错误ID: {error_id})")
            game_core.output("不用担心，你的进度已自动保存。")

    # 添加存档相关命令
    original_save_command = game_core._save_game if hasattr(game_core, "_save_game") else None

    def enhanced_save_game() -> None:
        """增强的保存游戏"""
        if game_core.game_state.player:
            save_id = tech_ops_system.create_game_save(game_core.game_state.to_dict(), "manual")
            game_core.output(f"游戏已保存 (存档ID: {save_id})")
        else:
            game_core.output("没有可保存的游戏进度")

    # 替换方法
    game_core.process_command = auto_save_wrapper
    if hasattr(game_core, "_save_game"):
        game_core._save_game = enhanced_save_game

    # 添加新方法
    game_core.list_saves = lambda: tech_ops_system.save_manager.list_saves()
    game_core.load_save = lambda save_id: tech_ops_system.load_game_save(save_id)
    game_core.get_system_status = tech_ops_system.get_system_status

    logger.info("技术功能已集成")


# 向后兼容的别名
class TechnicalOps(TechnicalOpsSystem):
    """`TechnicalOpsSystem` 的别名, 兼容旧代码"""

    pass
