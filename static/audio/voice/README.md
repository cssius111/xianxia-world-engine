# 语音文件 (Voice)

这个目录用于存放语音文件（未来扩展功能）。

## 规划中的语音功能

- 角色对话语音
- 系统提示语音
- 重要剧情语音
- NPC语音
- 旁白语音

## 语音文件规格

- 格式：MP3 或 WAV
- 采样率：44.1kHz
- 比特率：128kbps（MP3）
- 语言：中文普通话
- 音质：清晰，无杂音

## 命名规范

```
character_name_dialogue_id.mp3
例如：
- narrator_intro_001.mp3 (旁白-介绍-001)
- npc_elder_greeting_001.mp3 (NPC-长老-问候-001)
- system_levelup_001.mp3 (系统-升级-001)
```

## 实现建议

### 阶段一：文字转语音 (TTS)
- 使用在线TTS服务
- 选择合适的中文语音
- 批量生成常用语音

### 阶段二：真人录音
- 招募配音员
- 录制重要角色语音
- 后期处理和音效添加

## 技术集成

```javascript
// 播放语音示例
audioController.playVoice('narrator_intro_001.mp3');

// 带字幕的语音播放
audioController.playVoiceWithSubtitle('dialogue_text', 'voice_file.mp3');
```

## 存储优化

- 使用压缩格式减小文件大小
- 实现按需加载，避免一次性加载所有语音
- 考虑使用CDN分发大型语音文件

## 无障碍功能

- 提供语音开关选项
- 支持语音速度调节
- 兼容屏幕阅读器

## 注意事项

- 确保语音版权合规
- 控制总文件大小
- 考虑网络加载速度
- 提供静音选项

## 当前状态

🚧 **开发中** - 此功能尚未实现，仅作为未来扩展预留。
