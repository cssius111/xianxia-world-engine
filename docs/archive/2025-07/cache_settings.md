# 缓存与 TTL 设置

修仙世界引擎提供可调的缓存策略以提升性能。主要选项定义在 `config/game_config.py` 中，默认值如下：

- `data_cache_ttl`：`300` 秒。`DataLoader` 读取的文件在内存中的保存时间。
- `smart_cache_ttl`：`300` 秒。`SmartCache` 装饰器缓存结果的有效期。
- `smart_cache_size`：`128`。`SmartCache` 允许存放的最大条目数。

这些选项可以在初始化后通过修改 `config` 实例来调整，例如：

```python
from config.game_config import config

config.data_cache_ttl = 600       # 文件缓存 10 分钟
config.smart_cache_ttl = 60       # 智能缓存 1 分钟
config.smart_cache_size = 256     # 最大缓存 256 项
```

修改后重新启动游戏即可生效。
