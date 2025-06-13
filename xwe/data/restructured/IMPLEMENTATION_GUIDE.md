# 修仙世界引擎 - 开局体验与情报系统实现指南

## 概述

本文档说明如何集成双开局模式、角色创建系统、随机事件系统、情报公告系统、大事件时间轴和时间推进规则。

## 一、双开局模式实现

### 1.1 模式切换

通过命令行参数 `--mode` 控制：

```bash
# 开发模式
python main_menu.py --mode dev

# 玩家模式（默认）
python main_menu.py --mode player
```

### 1.2 模式差异

**开发模式特权：**
- 显示所有角色创建选项（包括隐藏出身）
- 可自定义属性数值（最高100）
- 解锁所有天赋选项
- 一键随机生成角色
- 可调用所有GM指令

**玩家模式限制：**
- 仅显示常规选项
- 属性随机范围限制（最高20）
- 天赋根据权重随机
- 需要满足解锁条件

## 二、角色创建流程

### 2.1 开局展示

1. **世界设定展示**
   - 读取 `world_setting.md`
   - 替换 `<WORLD_NAME>` 占位符
   - 以滚动文本形式展示

2. **角色创建界面**
   ```python
   # 伪代码示例
   def create_character(mode='player'):
       config = load_json('character_creation_config.json')
       
       # 根据模式调整选项
       if mode == 'dev':
           options = config['origins'] + config['hidden_origins']
       else:
           options = config['origins']
           
       # 展示选择界面
       selected_origin = ui.select("选择出身", options)
       selected_root = ui.select("选择灵根", config['spiritual_roots'])
       selected_traits = ui.multi_select("选择性格", config['personality_traits'], max=2)
       selected_talent = ui.select("选择天赋", config['initial_talents'])
       
       return Character(origin, root, traits, talent)
   ```

3. **随机ROLL集成**
   ```python
   # 与现有 character_roller.py 集成
   from xwe.core.roll_system.character_roller import CharacterRoller
   
   def random_with_constraints(constraints):
       roller = CharacterRoller()
       result = roller.roll()
       
       # 应用创建配置的约束
       if constraints.get('origin'):
           result.identity = constraints['origin']
       # ... 其他约束应用
       
       return result
   ```

## 三、随机事件系统

### 3.1 事件处理器

```python
class EventProcessor:
    def __init__(self):
        self.local_events = load_json('local_events.json')
        self.deepseek_client = DeepSeekClient()
        
    def generate_event(self, context):
        try:
            # 优先尝试 DeepSeek API
            event = self.deepseek_client.generate_event(context)
            return self.validate_event(event)
        except (TimeoutError, APIError):
            # 降级到本地事件库
            return self.get_local_event(context)
            
    def apply_event(self, event, game_state):
        effect = event['effect']
        
        if effect['type'] == 'stat_delta':
            for stat, delta in effect['payload'].items():
                game_state.player.stats[stat] += delta
                
        elif effect['type'] == 'boolean_flag':
            action = effect['payload']['action']
            flags = effect['payload']['flags']
            if action == 'set':
                game_state.flags.update(flags)
            else:
                game_state.flags.difference_update(flags)
                
        elif effect['type'] == 'item_reward':
            for item in effect['payload']['items']:
                game_state.inventory.add(item['id'], item['count'])
                
        # 记录到事件日志
        game_state.event_log.append({
            'timestamp': datetime.now(),
            'event': event
        })
```

### 3.2 DeepSeek 集成示例

```python
class DeepSeekClient:
    def generate_event(self, context, timeout=5):
        prompt = self._build_prompt(context)
        
        response = requests.post(
            self.api_url,
            json={'prompt': prompt, 'max_tokens': 500},
            timeout=timeout
        )
        
        event = self._parse_response(response.json())
        return self._validate_schema(event)
```

## 四、情报系统实现

### 4.1 数据模型

```python
class NewsItem:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.content = data['content']
        self.category = data['category']
        self.ttl = data['ttl']  # Time to live
        self.created_at = datetime.now()
        self.relevance_level = data['relevance_level']
        
    def is_expired(self):
        return (datetime.now() - self.created_at).seconds > self.ttl

class IntelligenceSystem:
    def __init__(self):
        self.global_news = []  # 全服共享
        self.personal_intel = {}  # 按玩家ID存储
        
    def add_global_news(self, news_item):
        self.global_news.append(news_item)
        self._cleanup_expired()
        
    def add_personal_intel(self, player_id, intel):
        if player_id not in self.personal_intel:
            self.personal_intel[player_id] = []
        self.personal_intel[player_id].append(intel)
```

### 4.2 UI 集成

```javascript
// 前端侧边栏实现
class NewsPanel {
    constructor() {
        this.currentTab = 'global';
    }
    
    render() {
        return `
        <div class="news-panel">
            <div class="tabs">
                <button onclick="switchTab('global')">修仙热点</button>
                <button onclick="switchTab('personal')">个人情报</button>
            </div>
            <div class="news-list">
                ${this.renderNewsList()}
            </div>
        </div>
        `;
    }
    
    onNewsClick(newsId) {
        // 显示详情弹窗
        const news = this.getNewsById(newsId);
        if (news.interactable_task_id) {
            // 可追踪任务
            showTaskTracker(news.interactable_task_id);
        }
    }
}
```

## 五、时间轴系统

### 5.1 时间管理器

```python
class TimelineManager:
    def __init__(self):
        self.events = load_json('timeline_events.json')
        self.current_date = GameDate(year=0, month=0, day=0)
        
    def advance_time(self, hours):
        self.current_date.add_hours(hours)
        triggered_events = self.check_triggers()
        return triggered_events
        
    def check_triggers(self):
        triggered = []
        for event in self.events['timeline_events']:
            if self.is_triggered(event):
                triggered.append(event)
        return triggered
        
    def is_triggered(self, event):
        event_date = self.parse_date(event['trigger_date'])
        if self.current_date >= event_date:
            # 检查其他条件
            if event.get('min_realm'):
                if not self.player_meets_realm(event['min_realm']):
                    return False
            return True
        return False
```

### 5.2 事件推送

```python
def push_timeline_event(event):
    # 转换为热点新闻
    news = {
        'id': f"timeline_{event['event_id']}",
        'title': event['name'],
        'content': event['description'],
        'category': '重大事件',
        'ttl': event.get('duration_days', 1) * 86400,
        'relevance_level': 10
    }
    
    # 推送到情报系统
    intelligence_system.add_global_news(NewsItem(news))
    
    # 触发游戏内效果
    if 'global_effects' in event:
        apply_global_effects(event['global_effects'])
```

## 六、时间推进集成

### 6.1 行动时间消耗

```python
import yaml

class TimeSystem:
    def __init__(self):
        with open('time_rules.yaml', 'r') as f:
            self.rules = yaml.safe_load(f)
            
    def get_time_cost(self, action, modifiers=None):
        base_cost = self.rules['default_time_cost'].get(
            action, 
            self.rules['deepseek_integration']['fallback_behavior']['default_cost']
        )
        
        if modifiers:
            for mod_type, mod_value in modifiers.items():
                if mod_type in self.rules['time_modifiers']:
                    base_cost *= self.rules['time_modifiers'][mod_type].get(mod_value, 1.0)
                    
        return base_cost
        
    def process_action(self, action, game_state):
        time_cost = self.get_time_cost(action, game_state.get_modifiers())
        
        # 应用疲劳系统
        if self.rules['special_rules']['fatigue_system']['enabled']:
            if game_state.active_hours > self.rules['special_rules']['fatigue_system']['threshold_hours']:
                time_cost *= self.rules['special_rules']['fatigue_system']['penalty_multiplier']
                
        # 推进时间
        timeline_manager.advance_time(time_cost)
        
        return time_cost
```

## 七、数据持久化

### 7.1 扩展 GameState

```python
class ExtendedGameState:
    def __init__(self, base_state):
        self.base = base_state
        self.event_log = []
        self.news_read = set()
        self.personal_intel = []
        self.timeline_progress = {}
        self.game_mode = 'player'
        
    def save(self):
        data = {
            'base': self.base.to_dict(),
            'event_log': self.event_log,
            'news_read': list(self.news_read),
            'personal_intel': self.personal_intel,
            'timeline_progress': self.timeline_progress,
            'game_mode': self.game_mode
        }
        save_json('game_state.json', data)
```

## 八、测试验证

### 8.1 测试脚本

```python
def test_game_modes():
    # 测试开发模式
    game_dev = GameEngine(mode='dev')
    assert game_dev.can_use_gm_commands() == True
    assert len(game_dev.get_character_options()) > 10
    
    # 测试玩家模式
    game_player = GameEngine(mode='player')
    assert game_player.can_use_gm_commands() == False
    assert len(game_player.get_character_options()) < 10

def test_event_system():
    processor = EventProcessor()
    
    # 测试本地事件
    event = processor.get_local_event({'level': 5})
    assert event['id'] in ['evt_village_help', 'evt_find_herbs']
    
    # 测试事件应用
    game_state = MockGameState()
    processor.apply_event(event, game_state)
    assert len(game_state.event_log) == 1

def test_timeline():
    timeline = TimelineManager()
    
    # 测试时间推进
    timeline.advance_time(24 * 30)  # 推进30天
    events = timeline.check_triggers()
    assert 'sect_recruit_qingyun' in [e['event_id'] for e in events]
```

## 九、注意事项

1. **性能优化**
   - 事件日志定期清理（保留最近1000条）
   - 过期新闻自动删除
   - DeepSeek API 调用缓存

2. **错误处理**
   - API 超时自动降级
   - 事件格式验证
   - 数据完整性检查

3. **扩展性**
   - 事件类型可扩展
   - 时间规则可配置
   - 模块化设计便于维护

## 十、部署清单

- [x] 创建所需的JSON/YAML配置文件
- [ ] 扩展现有 GameState 类
- [ ] 实现 EventProcessor 类  
- [ ] 实现 IntelligenceSystem 类
- [ ] 实现 TimelineManager 类
- [ ] 集成前端 UI 组件
- [ ] 编写单元测试
- [ ] 更新 API 文档

---

*本实现指南基于现有项目结构，所有新增功能均以扩展方式注入，不修改原有核心逻辑。*
