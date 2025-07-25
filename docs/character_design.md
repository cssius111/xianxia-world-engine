# 角色设计文档

## 八维属性系统

修仙世界采用独特的八维属性系统，每个属性范围为1-10：

### 核心属性

1. **悟性** (comprehension)
   - 影响修炼速度和功法领悟
   - 1-3: 愚钝 | 4-5: 普通 | 6-7: 聪慧 | 8-9: 天才 | 10: 妖孽

2. **根骨** (constitution)
   - 影响身体强度和生命值
   - 1-3: 孱弱 | 4-5: 普通 | 6-7: 强健 | 8-9: 天生神力 | 10: 金刚不坏

3. **气运** (fortune)
   - 影响机遇触发和宝物获得
   - 1-3: 霉运缠身 | 4-5: 普通 | 6-7: 小有福缘 | 8-9: 福星高照 | 10: 天选之子

4. **魅力** (charisma)
   - 影响NPC好感和社交事件
   - 1-3: 其貌不扬 | 4-5: 普通 | 6-7: 俊秀 | 8-9: 倾国倾城 | 10: 魅惑众生

5. **毅力** (willpower)
   - 影响心魔抵抗和困境突破
   - 1-3: 意志薄弱 | 4-5: 普通 | 6-7: 坚韧 | 8-9: 百折不挠 | 10: 道心永固

6. **感知** (perception)
   - 影响危险察觉和隐藏发现
   - 1-3: 迟钝 | 4-5: 普通 | 6-7: 敏锐 | 8-9: 洞察秋毫 | 10: 天眼通

7. **天命** (destiny)
   - 影响剧情走向和命运转折
   - 1-3: 命途多舛 | 4-5: 普通 | 6-7: 小有天命 | 8-9: 天命所归 | 10: 逆天改命

8. **机缘** (opportunity)
   - 影响奇遇频率和传承获得
   - 1-3: 无缘仙道 | 4-5: 普通 | 6-7: 机缘不断 | 8-9: 洞天福地 | 10: 大道垂青

## 保底机制

- **小保底**: 至少1项属性 ≥ 8
- **大保底**: 至少2项属性 ≥ 8

## 灵根系统

基础灵根：
- 金、木、水、火、土

特殊灵根：
- 雷、冰、风、光、暗

## 角色模板

### 剑修
- 特点：攻击力高，悟性和感知突出
- 推荐灵根：金、火、雷

### 体修
- 特点：防御力强，根骨和毅力突出
- 推荐灵根：土、金、木

### 符修
- 特点：变化多端，悟性和感知突出
- 推荐灵根：水、木、光

## 属性转换公式

将8维属性转换为游戏实际属性：

```
攻击力 = 基础值 + 根骨值
防御力 = 基础值 + 毅力值 / 2
生命值 = 基础值 + 根骨值 * 10
法力值 = 基础值 + 悟性值 * 5
暴击率 = 感知值 * 2%
闪避率 = 感知值 * 1.5%
```

## DeepSeek 提示词模板

```
你是 XianXiaCharacterParser，将以下中文设定转为 JSON 格式的角色数据。

输入描述：{user_input}

输出格式：
{
  "name": "角色名称",
  "age": 年龄(16-25),
  "spiritual_root": "灵根类型",
  "attributes": {
    "comprehension": 悟性(1-10),
    "constitution": 根骨(1-10),
    "fortune": 气运(1-10),
    "charisma": 魅力(1-10),
    "willpower": 毅力(1-10),
    "perception": 感知(1-10),
    "destiny": 天命(1-10),
    "opportunity": 机缘(1-10)
  }
}

请根据描述合理分配属性值，确保角色特色鲜明。
```

## 数据格式校验

使用 `xwe/data/restructured/character_schema.json` 可对生成的角色 JSON 文件进行校验，各字段支持 `null` 值。
