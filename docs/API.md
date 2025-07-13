# 修仙世界引擎 API 文档

## 概述

修仙世界引擎提供了完整的REST API接口，支持游戏状态管理、玩家交互和世界模拟。

## 认证

当前版本不需要认证，未来版本将支持JWT认证。

## API端点

### 游戏管理

#### 创建新游戏
- **URL**: `/api/game/new`
- **方法**: `POST`
- **请求体**:
```json
{
  "player_name": "玩家名称",
  "difficulty": "normal"
}
```
- **响应**:
```json
{
  "game_id": "uuid",
  "status": "created",
  "message": "游戏创建成功"
}
```

#### 获取游戏状态
- **URL**: `/api/game/<game_id>/state`
- **方法**: `GET`
- **响应**:
```json
{
  "player": {
    "name": "玩家名称",
    "realm": "练气期",
    "level": 1,
    "health": 100,
    "qi": 100
  },
  "location": "新手村",
  "time": "第1天"
}
```

### 玩家行为

#### 执行命令
- **URL**: `/api/game/<game_id>/command`
- **方法**: `POST`
- **请求体**:
```json
{
  "command": "修炼"
}
```
- **响应**:
```json
{
  "success": true,
  "message": "你开始修炼...",
  "state_changes": {}
}
```

### 修炼系统

#### 获取修炼状态
- **URL**: `/api/cultivation/status`
- **方法**: `GET`
- **响应**:
```json
{
  "realm": "练气期",
  "progress": 45.5,
  "next_realm": "筑基期",
  "tribulation_ready": false
}
```

### 成就系统

#### 获取成就列表
- **URL**: `/api/achievements/`
- **方法**: `GET`
- **响应**:
```json
{
  "achievements": [
    {
      "id": "first_cultivation",
      "name": "初入修行",
      "description": "完成第一次修炼",
      "unlocked": true,
      "unlocked_at": "2025-01-13T10:30:00Z"
    }
  ]
}
```

### 物品系统

#### 获取背包
- **URL**: `/api/inventory/`
- **方法**: `GET`
- **响应**:
```json
{
  "items": [
    {
      "id": "healing_pill",
      "name": "疗伤丹",
      "quantity": 5,
      "type": "consumable"
    }
  ],
  "capacity": 50,
  "used": 5
}
```

## 错误处理

所有API错误响应格式：
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

## 限流

- 所有API端点限制：100请求/分钟
- 超出限制返回429状态码

## WebSocket支持

游戏支持WebSocket连接用于实时更新：
- **URL**: `ws://localhost:5001/ws`
- **消息格式**: JSON

## 版本

当前API版本：v1
