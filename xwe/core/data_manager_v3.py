"""
数据统一加载-验证流程 —— DataManager V3
处理 restructured 目录下的核心JSON模块
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)

class DataManagerV3:
    """
    统一的数据管理器V3
    负责加载、验证和缓存所有游戏配置数据
    """
    
    # 单例模式
    _instance = None
    _cache: Dict[str, Dict] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.repo_root = Path(__file__).resolve().parents[2]
            self.data_dir = self.repo_root / "xwe" / "data" / "restructured"
            self._initialized = True
            logger.info(f"DataManagerV3 initialized with data_dir: {self.data_dir}")
    
    @classmethod
    def load(cls, name: str, *, refresh: bool = False) -> Dict[str, Any]:
        """
        加载指定的JSON配置文件
        
        Args:
            name: 配置名称（不含.json后缀），如 'combat_system'
            refresh: 是否强制刷新缓存
            
        Returns:
            解析并验证后的配置数据
        """
        instance = cls()
        
        # 检查缓存
        if name in cls._cache and not refresh:
            logger.debug(f"Loading {name} from cache")
            return cls._cache[name]
        
        # 文件路径
        file_path = instance.data_dir / f"{name}.json"
        schema_path = instance.data_dir / f"{name}_schema.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        logger.info(f"Loading configuration: {name}")
        
        try:
            # 加载JSON数据
            with open(file_path, 'r', encoding='utf-8') as f:
                payload = json.load(f)
            
            # 计算校验和
            content = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            checksum = hashlib.sha256(content.encode()).hexdigest()
            
            # 验证spec版本
            if "_spec_version" in payload and payload["_spec_version"] != "1.0.0":
                logger.warning(f"{name} spec version mismatch: {payload['_spec_version']} != 1.0.0")
            
            # 如果存在schema文件，进行验证
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                
                try:
                    validate(instance=payload, schema=schema)
                    logger.debug(f"{name} passed schema validation")
                except ValidationError as e:
                    logger.error(f"{name} schema validation failed: {e}")
                    raise
            else:
                logger.warning(f"No schema file found for {name}, skipping validation")
            
            # 校验checksum（如果存在）
            if "_checksum" in payload:
                if payload["_checksum"] != checksum:
                    logger.warning(f"{name} checksum mismatch, updating to: {checksum}")
                    payload["_checksum"] = checksum
            
            # 缓存数据
            cls._cache[name] = payload
            logger.info(f"Successfully loaded {name}")
            
            return payload
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading {name}: {e}")
            raise
    
    @classmethod
    def load_all(cls, refresh: bool = False) -> None:
        """
        按依赖顺序加载所有配置文件
        """
        logger.info("Loading all configurations...")
        
        # 定义加载顺序（考虑依赖关系）
        load_order = [
            "attribute_model",      # 基础属性模型
            "formula_library",      # 公式库
            "cultivation_realm",    # 境界系统
            "spiritual_root",       # 灵根系统
            "combat_system",        # 战斗系统
            "item_template",        # 物品模板
            "npc_template",         # NPC模板
            "event_template",       # 事件模板
            "faction_model",        # 门派模型
            "system_config"         # 系统配置
        ]
        
        for module_name in load_order:
            try:
                cls.load(module_name, refresh=refresh)
            except Exception as e:
                logger.error(f"Failed to load {module_name}: {e}")
                raise
        
        logger.info(f"Successfully loaded {len(cls._cache)} configurations")
    
    @classmethod
    def get(cls, path: str, default: Any = None) -> Any:
        """
        通过路径获取配置值
        
        Args:
            path: 点分隔的路径，如 'combat_system.damage_formulas.physical'
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        parts = path.split('.')
        module_name = parts[0]
        
        # 确保模块已加载
        if module_name not in cls._cache:
            try:
                cls.load(module_name)
            except:
                logger.warning(f"Failed to load module {module_name}")
                return default
        
        # 遍历路径
        current = cls._cache[module_name]
        for part in parts[1:]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    @classmethod
    def reload(cls, name: Optional[str] = None) -> None:
        """
        重新加载配置
        
        Args:
            name: 指定配置名称，如果为None则重新加载所有配置
        """
        if name:
            cls.load(name, refresh=True)
        else:
            cls.load_all(refresh=True)
    
    @classmethod
    def clear_cache(cls) -> None:
        """清空缓存"""
        cls._cache.clear()
        logger.info("Configuration cache cleared")
    
    @classmethod
    def get_loaded_modules(cls) -> list[str]:
        """获取已加载的模块列表"""
        return list(cls._cache.keys())
    
    @classmethod
    def validate_dependencies(cls) -> Dict[str, list[str]]:
        """
        验证配置之间的依赖关系
        
        Returns:
            依赖检查结果，包含任何缺失的依赖
        """
        issues = {}
        
        # 检查公式库中引用的属性
        if "formula_library" in cls._cache and "attribute_model" in cls._cache:
            formulas = cls._cache["formula_library"].get("formulas", [])
            defined_attrs = cls._cache["attribute_model"].get("attributes", {})
            
            for formula in formulas:
                if "input_vars" in formula:
                    for var in formula["input_vars"]:
                        # 检查变量是否在属性模型中定义
                        if var not in defined_attrs and not var.startswith(("skill", "buff", "item")):
                            if formula["id"] not in issues:
                                issues[formula["id"]] = []
                            issues[formula["id"]].append(f"Undefined variable: {var}")
        
        return issues


# 导出便捷接口
DM = DataManagerV3()

# 与旧版接口兼容的别名
DataManager = DataManagerV3

def load_game_data():
    """加载所有游戏数据的便捷函数"""
    DM.load_all()

def get_config(path: str, default: Any = None) -> Any:
    """获取配置的便捷函数"""
    return DM.get(path, default)
