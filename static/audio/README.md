# 音频文件说明

请在此目录下放置背景音乐文件，支持的格式：
- MP3
- OGG
- WAV

建议文件名：
- bgm1.mp3
- bgm2.mp3
- bgm3.mp3
- ...

音乐会在游戏开始时随机播放。

## 推荐的免费音乐资源

1. **Free Music Archive**
   - https://freemusicarchive.org/
   - 大量免费音乐，注意查看许可证

2. **YouTube Audio Library**
   - https://www.youtube.com/audiolibrary
   - Google提供的免费音乐库

3. **Incompetech**
   - https://incompetech.com/
   - Kevin MacLeod的免费音乐

4. **Bensound**
   - https://www.bensound.com/
   - 免费背景音乐

## 音乐文件要求

- 文件大小：建议不超过10MB
- 比特率：128-192 kbps
- 时长：2-5分钟循环播放效果较好

## 修改音乐列表

如需修改音乐列表，请编辑 `templates_enhanced/components/welcome_modal_v2.html` 中的：

```javascript
musicList: [
    '/static/audio/bgm1.mp3',
    '/static/audio/bgm2.mp3',
    '/static/audio/bgm3.mp3'
]
```