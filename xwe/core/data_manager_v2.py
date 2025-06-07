"""
数据统一加载-验证流程 - DataManagerV2
负责加载和验证 restructured 目录下的所有JSON数据
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)

# 获取项目根目录
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "xwe" / "data" / "restructured"


class DataManagerV2:
    """
    统一的数据管理器，负责：
    1. 加载所有JSON数据文件
    2. 验证数据格式（JSON Schema）
    3. 缓存数据以提高性能
    4. 处理数据依赖关系
    """
    
    _cache: Dict[str, Dict[str, Any]] = {}
    _checksums: Dict[str, str] = {}
    _loaded_modules = set()
    
    # 定义加载顺序（处理依赖关系）
    LOAD_ORDER = [
        "attribute_model",      # 基础属性定义
        "formula_library",      # 公式库
        "cultivation_realm",    # 依赖属性
        "spiritual_root",       # 依赖属性
        "combat_system",        # 依赖属性、公式
        "item_template",        # 独立模块
        "npc_template",         # 依赖属性
        "event_template",       # 依赖NPC、物品
        "faction_model",        # 依赖NPC、技能
        "system_config"         # 全局配置
    ]
    
    @classmethod
    def initialize(cls) -> None:
        """初始化数据管理器，按顺序加载所有数据"""
        logger.info("Initializing DataManagerV2...")
        
        for module_name in cls.LOAD_ORDER:
            try:
                cls.load(module_name)
                logger.info(f"Successfully loaded: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load {module_name}: {e}")
                raise
                
        logger.info(f"DataManagerV2 initialized. Loaded {len(cls._loaded_modules)} modules.")
    
    @classmethod
    def load(cls, name: str, *, refresh: bool = False) -> Dict[str, Any]:
        """
        加载指定的数据模块
        
        Args:
            name: 模块名称（不含.json后缀）
            refresh: 是否强制刷新缓存
            
        Returns:
            加载的数据字典
        """
        # 检查缓存
        if name in cls._cache and not refresh:
            return cls._cache[name]
        
        # 文件路径
        data_file = DATA_DIR / f"{name}.json"
        schema_file = DATA_DIR / f"{name}_schema.json"
        
        # 检查文件是否存在
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
            
        # 加载数据
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {name}.json: {e}")
            
        # 计算校验和
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        checksum = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
        
        # 版本检查
        if "meta" in data:
            version = data["meta"].get("version", "unknown")
            logger.debug(f"Loading {name} version {version}")
            
        # Schema验证
        if schema_file.exists():
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                validate(instance=data, schema=schema)
                logger.debug(f"Schema validation passed for {name}")
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid schema file for {name}: {e}")
            except ValidationError as e:
                raise ValueError(f"Schema validation failed for {name}: {e}")
        else:
            logger.warning(f"No schema file found for {name}")
            
        # 存储数据和校验和
        cls._cache[name] = data
        cls._checksums[name] = checksum
        cls._loaded_modules.add(name)
        
        return data
    
    @classmethod
    def get(cls, module: str, path: str = None, default: Any = None) -> Any:
        """
        获取数据
        
        Args:
            module: 模块名称
            path: 数据路径（用.分隔），如 "primary_attributes.strength"
            default: 默认值
            
        Returns:
            请求的数据
        """
        if module not in cls._cache:
            cls.load(module)
            
        data = cls._cache[module]
        
        if path:
            # 按路径导航
            parts = path.split('.')
            for part in parts:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                elif isinstance(data, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(data):
                        data = data[index]
                    else:
                        return default
                else:
                    return default
                    
        return data
    
    @classmethod
    def get_formula(cls, formula_id: str) -> Optional[Dict[str, Any]]:
        """
        获取公式定义
        
        Args:
            formula_id: 公式ID
            
        Returns:
            公式定义字典
        """
        formulas = cls.get("formula_library", "formulas", {})
        return formulas.get(formula_id)
    
    @classmethod
    def get_attribute_definition(cls, attr_name: str) -> Optional[Dict[str, Any]]:
        """获取属性定义"""
        # 先检查主要属性
        primary = cls.get("attribute_model", f"primary_attributes.{attr_name}")
        if primary:
            return primary
            
        # 检查修炼属性
        cultivation = cls.get("attribute_model", f"cultivation_attributes.{attr_name}")
        if cultivation:
            return cultivation
            
        # 检查衍生属性
        derived = cls.get("attribute_model", f"derived_attributes.{attr_name}")
        return derived
    
    @classmethod
    def get_realm_info(cls, realm_id: str) -> Optional[Dict[str, Any]]:
        """获取境界信息"""
        realms = cls.get("cultivation_realm", "realms", [])
        for realm in realms:
            if realm.get("id") == realm_id:
                return realm
        return None
    
    @classmethod
    def get_item_template(cls, item_id: str) -> Optional[Dict[str, Any]]:
        """获取物品模板"""
        items = cls.get("item_template", "item_templates", [])
        for item in items:
            if item.get("id") == item_id:
                return item
        return None
    
    @classmethod
    def get_npc_template(cls, npc_id: str) -> Optional[Dict[str, Any]]:
        """获取NPC模板"""
        npcs = cls.get("npc_template", "npc_templates", [])
        for npc in npcs:
            if npc.get("id") == npc_id:
                return npc
        return None
    
    @classmethod
    def reload_all(cls) -> None:
        """重新加载所有数据（用于开发模式）"""
        cls._cache.clear()
        cls._checksums.clear()
        cls._loaded_modules.clear()
        cls.initialize()
    
    @classmethod
    def get_loaded_modules(cls) -> list:
        """获取已加载的模块列表"""
        return list(cls._loaded_modules)
    
    @classmethod
    def verify_integrity(cls) -> Dict[str, bool]:
        """验证所有数据的完整性"""
        results = {}
        
        for module in cls.LOAD_ORDER:
            try:
                # 重新计算校验和
                data = cls._cache.get(module)
                if data:
                    data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
                    current_checksum = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
                    stored_checksum = cls._checksums.get(module)
                    results[module] = current_checksum == stored_checksum
                else:
                    results[module] = False
            except Exception as e:
                logger.error(f"Integrity check failed for {module}: {e}")
                results[module] = False
                
        return results


# 便捷访问函数
def get_data(module: str, path: str = None, default: Any = None) -> Any:
    """便捷函数：获取数据"""
    return DataManagerV2.get(module, path, default)


def get_formula(formula_id: str) -> Optional[Dict[str, Any]]:
    """便捷函数：获取公式"""
    return DataManagerV2.get_formula(formula_id)


def init_data():
    """便捷函数：初始化数据管理器"""
    DataManagerV2.initialize()


if __name__ == "__main__":
    # 测试代码
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        # 初始化
        DataManagerV2.initialize()
        
        # 测试获取数据
        print("\n=== 测试数据获取 ===")
        
        # 获取属性定义
        strength = DataManagerV2.get_attribute_definition("strength")
        print(f"力量属性: {strength['name']} - {strength['description']}")
        
        # 获取境界信息
        qi_gathering = DataManagerV2.get_realm_info("qi_gathering")
        print(f"聚气期: {qi_gathering['name']} - 等级数: {qi_gathering['levels']}")
        
        # 获取公式
        health_formula = DataManagerV2.get_formula("health_calculation")
        print(f"生命值公式: {health_formula['expression']}")
        
        # 验证完整性
        print("\n=== 数据完整性检查 ===")
        integrity = DataManagerV2.verify_integrity()
        for module, is_valid in integrity.items():
            status = "✓" if is_valid else "✗"
            print(f"{status} {module}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
