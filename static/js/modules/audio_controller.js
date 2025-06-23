/**
 * 修仙世界模拟器 - 音频控制器
 * 负责游戏音效和背景音乐的管理
 */

class XianxiaAudioController {
    constructor(gameController) {
        this.game = gameController;
        this.audioContext = null;
        this.audioBuffers = new Map();
        this.activeSounds = new Map();
        this.musicQueue = [];
        this.currentMusic = null;
        
        this.settings = {
            masterVolume: 0.7,
            musicVolume: 0.5,
            sfxVolume: 0.8,
            ambientVolume: 0.4,
            enabled: true
        };
        
        this.soundCategories = {
            music: [],
            sfx: [],
            ambient: [],
            voice: []
        };
        
        this.init();
    }
    
    /**
     * 初始化音频控制器
     */
    async init() {
        console.log('🎵 音频控制器初始化中...');
        
        try {
            // 初始化Web Audio API
            await this.initializeAudioContext();
            
            // 加载音频设置
            this.loadAudioSettings();
            
            // 获取可用音频文件
            await this.loadAudioFiles();
            
            // 设置音频事件监听
            this.setupAudioEvents();
            
            // 创建音频控制UI
            this.createAudioControls();
            
            console.log('✅ 音频控制器初始化完成');
        } catch (error) {
            console.error('❌ 音频控制器初始化失败:', error);
            this.settings.enabled = false;
        }
    }
    
    /**
     * 初始化音频上下文
     */
    async initializeAudioContext() {
        // 尝试创建AudioContext
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // 检查音频上下文状态
            if (this.audioContext.state === 'suspended') {
                console.log('音频上下文已暂停，等待用户交互...');
                
                // 添加用户交互监听器来激活音频
                this.addUserInteractionListener();
            }
        } catch (error) {
            console.error('创建音频上下文失败:', error);
            throw error;
        }
    }
    
    /**
     * 添加用户交互监听器
     */
    addUserInteractionListener() {
        const resumeAudio = async () => {
            if (this.audioContext && this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
                console.log('音频上下文已激活');
                
                // 播放欢迎音效
                this.playWelcomeSound();
            }
            
            // 移除监听器
            document.removeEventListener('click', resumeAudio);
            document.removeEventListener('keydown', resumeAudio);
        };
        
        document.addEventListener('click', resumeAudio);
        document.addEventListener('keydown', resumeAudio);
    }
    
    /**
     * 加载音频设置
     */
    loadAudioSettings() {
        const savedSettings = localStorage.getItem('xianxia_audio_settings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                this.settings = { ...this.settings, ...settings };
            } catch (error) {
                console.error('加载音频设置失败:', error);
            }
        }
    }
    
    /**
     * 保存音频设置
     */
    saveAudioSettings() {
        try {
            localStorage.setItem('xianxia_audio_settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('保存音频设置失败:', error);
        }
    }
    
    /**
     * 获取可用音频文件
     */
    async loadAudioFiles() {
        try {
            const response = await fetch('/get_audio_list');
            const data = await response.json();
            
            // 分类音频文件
            this.categorizeAudioFiles(data.files);
            
            // 预加载重要音频
            await this.preloadCriticalAudio();
            
        } catch (error) {
            console.error('获取音频文件列表失败:', error);
        }
    }
    
    /**
     * 分类音频文件
     */
    categorizeAudioFiles(files) {
        files.forEach(filename => {
            const lowerName = filename.toLowerCase();
            
            if (lowerName.includes('music') || lowerName.includes('bgm')) {
                this.soundCategories.music.push(filename);
            } else if (lowerName.includes('sfx') || lowerName.includes('sound')) {
                this.soundCategories.sfx.push(filename);
            } else if (lowerName.includes('ambient')) {
                this.soundCategories.ambient.push(filename);
            } else if (lowerName.includes('voice')) {
                this.soundCategories.voice.push(filename);
            } else {
                // 默认归类为音效
                this.soundCategories.sfx.push(filename);
            }
        });
        
        console.log('音频文件分类完成:', this.soundCategories);
    }
    
    /**
     * 预加载关键音频
     */
    async preloadCriticalAudio() {
        const criticalSounds = [
            'click.mp3',
            'command.mp3', 
            'welcome.mp3',
            'error.mp3',
            'success.mp3'
        ];
        
        for (const soundFile of criticalSounds) {
            if (this.soundCategories.sfx.includes(soundFile)) {
                await this.loadAudioBuffer(soundFile);
            }
        }
    }
    
    /**
     * 加载音频缓冲区
     */
    async loadAudioBuffer(filename) {
        if (this.audioBuffers.has(filename)) {
            return this.audioBuffers.get(filename);
        }
        
        try {
            const response = await fetch(`/static/audio/${filename}`);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            this.audioBuffers.set(filename, audioBuffer);
            return audioBuffer;
            
        } catch (error) {
            console.error(`加载音频文件失败: ${filename}`, error);
            return null;
        }
    }
    
    /**
     * 播放音效
     */
    async playSound(filename, options = {}) {
        if (!this.settings.enabled || !this.audioContext) {
            return null;
        }
        
        try {
            // 加载音频缓冲区
            let buffer = this.audioBuffers.get(filename);
            if (!buffer) {
                buffer = await this.loadAudioBuffer(filename);
                if (!buffer) return null;
            }
            
            // 创建音频源
            const source = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            
            source.buffer = buffer;
            
            // 设置音量
            const volume = (options.volume || 1) * this.settings.sfxVolume * this.settings.masterVolume;
            gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime);
            
            // 连接音频节点
            source.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // 播放音频
            source.start(0);
            
            // 记录活跃音频
            const soundId = Date.now() + Math.random();
            this.activeSounds.set(soundId, { source, gainNode, filename });
            
            // 音频结束时清理
            source.onended = () => {
                this.activeSounds.delete(soundId);
            };
            
            return soundId;
            
        } catch (error) {
            console.error(`播放音效失败: ${filename}`, error);
            return null;
        }
    }
    
    /**
     * 播放背景音乐
     */
    async playMusic(filename, options = {}) {
        if (!this.settings.enabled || !this.audioContext) {
            return;
        }
        
        // 停止当前音乐
        this.stopMusic();
        
        try {
            let buffer = this.audioBuffers.get(filename);
            if (!buffer) {
                buffer = await this.loadAudioBuffer(filename);
                if (!buffer) return;
            }
            
            const source = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            
            source.buffer = buffer;
            source.loop = options.loop !== false; // 默认循环播放
            
            // 设置音量
            const volume = (options.volume || 1) * this.settings.musicVolume * this.settings.masterVolume;
            gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime);
            
            // 淡入效果
            if (options.fadeIn) {
                gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(volume, this.audioContext.currentTime + options.fadeIn);
            }
            
            source.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            source.start(0);
            
            this.currentMusic = { source, gainNode, filename };
            
            source.onended = () => {
                this.currentMusic = null;
            };
            
        } catch (error) {
            console.error(`播放背景音乐失败: ${filename}`, error);
        }
    }
    
    /**
     * 停止背景音乐
     */
    stopMusic(fadeOut = false) {
        if (!this.currentMusic) return;
        
        if (fadeOut) {
            // 淡出效果
            const fadeTime = typeof fadeOut === 'number' ? fadeOut : 1.0;
            const now = this.audioContext.currentTime;
            
            this.currentMusic.gainNode.gain.setValueAtTime(
                this.currentMusic.gainNode.gain.value, now
            );
            this.currentMusic.gainNode.gain.linearRampToValueAtTime(0, now + fadeTime);
            
            setTimeout(() => {
                if (this.currentMusic) {
                    this.currentMusic.source.stop();
                    this.currentMusic = null;
                }
            }, fadeTime * 1000);
        } else {
            this.currentMusic.source.stop();
            this.currentMusic = null;
        }
    }
    
    /**
     * 设置音频事件监听
     */
    setupAudioEvents() {
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAudio();
            } else {
                this.resumeAudio();
            }
        });
        
        // 监听窗口焦点变化
        window.addEventListener('blur', () => this.pauseAudio());
        window.addEventListener('focus', () => this.resumeAudio());
    }
    
    /**
     * 暂停音频
     */
    pauseAudio() {
        if (this.audioContext && this.audioContext.state === 'running') {
            this.audioContext.suspend();
        }
    }
    
    /**
     * 恢复音频
     */
    resumeAudio() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
    }
    
    /**
     * 创建音频控制UI
     */
    createAudioControls() {
        const controls = document.createElement('div');
        controls.className = 'audio-controls';
        controls.innerHTML = `
            <button class="audio-toggle" title="${this.settings.enabled ? '关闭音效' : '开启音效'}">
                ${this.settings.enabled ? '🔊' : '🔇'}
            </button>
        `;
        
        document.body.appendChild(controls);
        
        // 绑定事件
        const toggleButton = controls.querySelector('.audio-toggle');
        toggleButton.addEventListener('click', () => this.toggleAudio());
    }
    
    /**
     * 切换音频开关
     */
    toggleAudio() {
        this.settings.enabled = !this.settings.enabled;
        
        if (!this.settings.enabled) {
            this.stopAllSounds();
            this.stopMusic();
        }
        
        // 更新UI
        const toggleButton = document.querySelector('.audio-toggle');
        if (toggleButton) {
            toggleButton.textContent = this.settings.enabled ? '🔊' : '🔇';
            toggleButton.title = this.settings.enabled ? '关闭音效' : '开启音效';
        }
        
        // 保存设置
        this.saveAudioSettings();
        
        console.log('音频已', this.settings.enabled ? '开启' : '关闭');
    }
    
    /**
     * 停止所有音效
     */
    stopAllSounds() {
        this.activeSounds.forEach(sound => {
            try {
                sound.source.stop();
            } catch (error) {
                // 忽略已经停止的音频
            }
        });
        
        this.activeSounds.clear();
    }
    
    /**
     * 设置主音量
     */
    setMasterVolume(volume) {
        this.settings.masterVolume = Math.max(0, Math.min(1, volume));
        this.saveAudioSettings();
    }
    
    /**
     * 设置音乐音量
     */
    setMusicVolume(volume) {
        this.settings.musicVolume = Math.max(0, Math.min(1, volume));
        
        // 更新当前播放的音乐音量
        if (this.currentMusic) {
            const newVolume = volume * this.settings.masterVolume;
            this.currentMusic.gainNode.gain.setValueAtTime(
                newVolume, this.audioContext.currentTime
            );
        }
        
        this.saveAudioSettings();
    }
    
    /**
     * 设置音效音量
     */
    setSfxVolume(volume) {
        this.settings.sfxVolume = Math.max(0, Math.min(1, volume));
        this.saveAudioSettings();
    }
    
    /**
     * 播放特定游戏音效
     */
    async playWelcomeSound() {
        await this.playSound('welcome.mp3', { volume: 0.8 });
    }
    
    async playClickSound() {
        await this.playSound('click.mp3', { volume: 0.6 });
    }
    
    async playCommandSound() {
        await this.playSound('command.mp3', { volume: 0.7 });
    }
    
    async playErrorSound() {
        await this.playSound('error.mp3', { volume: 0.8 });
    }
    
    async playSuccessSound() {
        await this.playSound('success.mp3', { volume: 0.7 });
    }
    
    async playLevelUpSound() {
        await this.playSound('levelup.mp3', { volume: 0.9 });
    }
    
    async playCombatSound() {
        await this.playSound('combat.mp3', { volume: 0.8 });
    }
    
    /**
     * 播放随机背景音乐
     */
    async playRandomMusic() {
        if (this.soundCategories.music.length === 0) return;
        
        const randomIndex = Math.floor(Math.random() * this.soundCategories.music.length);
        const musicFile = this.soundCategories.music[randomIndex];
        
        await this.playMusic(musicFile, { 
            loop: true, 
            fadeIn: 2.0,
            volume: 0.3 
        });
    }
    
    /**
     * 播放氛围音效
     */
    async playAmbientSound(location) {
        const ambientMap = {
            '青云城': 'city_ambient.mp3',
            '修炼室': 'meditation_ambient.mp3',
            '山林': 'forest_ambient.mp3',
            '洞府': 'cave_ambient.mp3'
        };
        
        const ambientFile = ambientMap[location];
        if (ambientFile && this.soundCategories.ambient.includes(ambientFile)) {
            await this.playSound(ambientFile, { 
                volume: this.settings.ambientVolume,
                loop: true 
            });
        }
    }
    
    /**
     * 根据游戏状态播放音乐
     */
    playContextualMusic(context) {
        const musicMap = {
            'welcome': 'welcome_theme.mp3',
            'exploration': 'exploration_theme.mp3',
            'combat': 'combat_theme.mp3',
            'meditation': 'meditation_theme.mp3',
            'victory': 'victory_theme.mp3',
            'defeat': 'defeat_theme.mp3'
        };
        
        const musicFile = musicMap[context];
        if (musicFile && this.soundCategories.music.includes(musicFile)) {
            this.playMusic(musicFile, { 
                fadeIn: 1.5,
                volume: 0.4 
            });
        }
    }
    
    /**
     * 创建音频可视化
     */
    createAudioVisualizer() {
        if (!this.audioContext) return;
        
        const analyser = this.audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        // 连接分析器
        if (this.currentMusic) {
            this.currentMusic.gainNode.connect(analyser);
        }
        
        // 这里可以添加可视化绘制代码
        return { analyser, dataArray };
    }
    
    /**
     * 检查音频是否启用
     */
    isEnabled() {
        return this.settings.enabled;
    }
    
    /**
     * 获取音频设置
     */
    getSettings() {
        return { ...this.settings };
    }
    
    /**
     * 获取音频统计信息
     */
    getAudioStats() {
        return {
            enabled: this.settings.enabled,
            contextState: this.audioContext?.state,
            activeSounds: this.activeSounds.size,
            loadedBuffers: this.audioBuffers.size,
            currentMusic: this.currentMusic?.filename || null,
            categories: {
                music: this.soundCategories.music.length,
                sfx: this.soundCategories.sfx.length,
                ambient: this.soundCategories.ambient.length,
                voice: this.soundCategories.voice.length
            }
        };
    }
    
    /**
     * 销毁音频控制器
     */
    destroy() {
        // 停止所有音频
        this.stopAllSounds();
        this.stopMusic();
        
        // 关闭音频上下文
        if (this.audioContext) {
            this.audioContext.close();
        }
        
        // 清理缓存
        this.audioBuffers.clear();
        this.activeSounds.clear();
        
        // 移除UI控制
        const controls = document.querySelector('.audio-controls');
        if (controls) {
            controls.remove();
        }
        
        console.log('🎵 音频控制器已销毁');
    }
}

// 导出供其他模块使用
window.XianxiaAudioController = XianxiaAudioController;