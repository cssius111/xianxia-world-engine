
# 确保监控器正确初始化
import os
os.environ['ENABLE_PROMETHEUS'] = 'true'

# 预初始化监控器
from xwe.core.nlp.monitor import get_nlp_monitor
monitor = get_nlp_monitor()
