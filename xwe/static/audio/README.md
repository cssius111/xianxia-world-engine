# 音频文件说明

这个目录包含修仙世界模拟器的所有音频文件。

## 目录结构

```
audio/
├── sfx/                    # 音效文件
│   ├── click.mp3          # 点击音效
│   ├── command.mp3        # 命令音效
│   ├── success.mp3        # 成功音效
│   ├── error.mp3          # 错误音效
│   ├── levelup.mp3        # 升级音效
│   └── combat.mp3         # 战斗音效
├── music/                  # 背景音乐
│   ├── welcome_theme.mp3  # 欢迎主题
│   ├── game_theme.mp3     # 游戏主题
│   ├── combat_theme.mp3   # 战斗主题
│   └── meditation_theme.mp3 # 修炼主题
├── ambient/               # 环境音效
│   ├── city_ambient.mp3   # 城市环境音
│   ├── forest_ambient.mp3 # 森林环境音
│   └── cave_ambient.mp3   # 洞穴环境音
└── voice/                 # 语音文件（未来扩展）
```

## 音频格式

- 推荐使用 MP3 格式（兼容性好）
- 音效文件大小控制在 100KB 以内
- 背景音乐可以适当大一些，但建议不超过 5MB
- 采样率 44.1kHz，比特率 128kbps

## 添加新音频

1. 将音频文件放入对应的子目录
2. 文件名使用英文，格式为 `action_description.mp3`
3. 在 `audio_controller.js` 中添加对应的播放函数

## 版权说明

请确保所有音频文件都有合法的使用权限。
建议使用免费的音频资源或自制音频。
