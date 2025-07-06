/**
 * 修仙世界模拟器 - 主控制器
 * 负责整体游戏流程控制和模块协调
 */

class XianxiaGameController {
    constructor() {
        this.isDebugMode = false;
        this.gameState = {
            isPlaying: false,
            player: null,
            currentLocation: null,
            logs: [],
            lastUpdate: Date.now()
        };
        
        this.modules = {
            ui: null,
            audio: null,
            profile: null,
            modal: null,
            debug: null
        };
        
        this.settings = {
            autoSave: true,
            soundEnabled: true,
            musicEnabled: true,
            animationEnabled: true,
            debugMode: false
        };

        this.eventSource = null;
        this.gameUpdateInterval = null;
        
        this.init();
    }
    
    /**
     * 初始化游戏控制器
     */
    init() {
        console.log('🎮 修仙世界模拟器启动中...');
        
        // 检测开发者模式
        this.checkDebugMode();
        
        // 初始化事件监听
        this.setupEventListeners();
        
        // 初始化游戏状态
        this.loadGameSettings();
        
        // 启动游戏循环
        this.startGameLoop();
        
        console.log('✅ 游戏控制器初始化完成');
    }
    
    /**
     * 检测开发者模式
     */
    checkDebugMode() {
        const urlParams = new URLSearchParams(window.location.search);
        const storageDebug = localStorage.getItem('dev');
        const sessionDebug = sessionStorage.getItem('dev_mode');

        this.isDebugMode =
            urlParams.get('dev') === 'true' ||
            storageDebug === 'true' ||
            urlParams.get('mode') === 'dev' ||
            sessionDebug === 'true';
        
        if (this.isDebugMode) {
            document.body.classList.add('dev-mode');
            console.log('🔧 开发者模式已启用');
            this.enableDebugMode();
        }
    }
    
    /**
     * 启用开发者模式
     */
    enableDebugMode() {
        // 创建调试控制台
        this.createDebugConsole();
        
        // 暴露调试API
        window.XWE_DEBUG = {
            game: this,
            getState: () => this.gameState,
            setDebug: (enabled) => this.setDebugMode(enabled),
            clearLogs: () => this.clearGameLogs(),
            exportSave: () => this.exportGameData(),
            importSave: (data) => this.importGameData(data)
        };
        
        // 启用详细日志
        this.enableVerboseLogging();
    }
    
    /**
     * 创建调试控制台
     */
    createDebugConsole() {
        const console = document.createElement('div');
        console.className = 'dev-console';
        console.innerHTML = `
            <div style="border-bottom: 1px solid #444; padding-bottom: 5px; margin-bottom: 5px;">
                <strong>🔧 开发者控制台</strong>
                <button onclick="this.parentElement.parentElement.style.display='none'" 
                        style="float: right; background: none; border: none; color: white; cursor: pointer;">×</button>
            </div>
            <div id="debug-logs" style="font-size: 0.7rem; max-height: 150px; overflow-y: auto;"></div>
        `;
        document.body.appendChild(console);
        
        this.debugConsole = console.querySelector('#debug-logs');
    }
    
    /**
     * 启用详细日志
     */
    enableVerboseLogging() {
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;
        
        console.log = (...args) => {
            originalLog.apply(console, args);
            this.addDebugLog('LOG', args.join(' '));
        };
        
        console.error = (...args) => {
            originalError.apply(console, args);
            this.addDebugLog('ERROR', args.join(' '));
        };
        
        console.warn = (...args) => {
            originalWarn.apply(console, args);
            this.addDebugLog('WARN', args.join(' '));
        };
    }
    
    /**
     * 添加调试日志
     */
    addDebugLog(type, message) {
        if (!this.debugConsole) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.innerHTML = `<span style="color: #666;">[${timestamp}]</span> <span style="color: ${this.getLogColor(type)};">${type}</span>: ${message}`;
        
        this.debugConsole.appendChild(logEntry);
        this.debugConsole.scrollTop = this.debugConsole.scrollHeight;
        
        // 限制日志数量
        while (this.debugConsole.children.length > 100) {
            this.debugConsole.removeChild(this.debugConsole.firstChild);
        }
    }
    
    /**
     * 获取日志颜色
     */
    getLogColor(type) {
        const colors = {
            'LOG': '#00ff00',
            'ERROR': '#ff0000',
            'WARN': '#ffff00',
            'INFO': '#00ffff'
        };
        return colors[type] || '#ffffff';
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 页面加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
        
        // 页面卸载前保存
        window.addEventListener('beforeunload', () => this.onBeforeUnload());
        
        // 窗口焦点变化
        window.addEventListener('focus', () => this.onWindowFocus());
        window.addEventListener('blur', () => this.onWindowBlur());
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // 全局错误处理
        window.addEventListener('error', (e) => this.handleGlobalError(e));
        window.addEventListener('unhandledrejection', (e) => this.handleUnhandledRejection(e));
    }
    
    /**
     * DOM准备就绪
     */
    onDOMReady() {
        console.log('📄 DOM已准备就绪');
        
        // 初始化UI模块
        this.initializeModules();
        
        // 检查游戏状态
        this.checkGameState();
        
        // 显示欢迎信息
        this.showWelcomeMessage();
    }
    
    /**
     * 初始化所有模块
     */
    initializeModules() {
        try {
            // 初始化UI控制器
            if (window.XianxiaUIController) {
                this.modules.ui = new XianxiaUIController(this);
                console.log('✅ UI模块初始化完成');
            }
            
            // 初始化音频控制器
            if (window.XianxiaAudioController) {
                this.modules.audio = new XianxiaAudioController(this);
                console.log('✅ 音频模块初始化完成');
            }
            
            // 初始化角色管理器
            if (window.XianxiaPlayerProfile) {
                this.modules.profile = new XianxiaPlayerProfile(this);
                console.log('✅ 角色模块初始化完成');
            }
            
            // 初始化模态框控制器
            if (window.XianxiaModalController) {
                this.modules.modal = new XianxiaModalController(this);
                console.log('✅ 模态框模块初始化完成');
            }
            
        } catch (error) {
            console.error('❌ 模块初始化失败:', error);
            this.showErrorMessage('模块初始化失败，请刷新页面重试');
        }
    }
    
    /**
     * 检查游戏状态
     */
    checkGameState() {
        // 检查是否有进行中的游戏
        const gameInProgress = this.checkGameInProgress();
        
        if (gameInProgress) {
            this.gameState.isPlaying = true;
            this.startGameUpdates();
        }
        
        // 检查是否需要显示教程
        const showTutorial = this.shouldShowTutorial();
        
        if (showTutorial) {
            this.showTutorial();
        }
    }
    
    /**
     * 检查游戏是否正在进行
     */
    checkGameInProgress() {
        const gameElement = document.querySelector('.game-output');
        return gameElement && gameElement.children.length > 0;
    }
    
    /**
     * 是否显示教程
     */
    shouldShowTutorial() {
        const tutorialShown = localStorage.getItem('tutorial_shown');
        const isNewSession = document.body.dataset.newSession === 'true';
        
        return !tutorialShown && isNewSession;
    }
    
    /**
     * 显示教程
     */
    showTutorial() {
        if (this.modules.modal) {
            this.modules.modal.showTutorial();
        }
        
        localStorage.setItem('tutorial_shown', 'true');
    }
    
    /**
     * 显示欢迎信息
     */
    showWelcomeMessage() {
        if (this.isDebugMode) {
            console.log('🎉 欢迎来到修仙世界模拟器 (开发者模式)');
        } else {
            console.log('🎉 欢迎来到修仙世界模拟器');
        }
        
        // 播放欢迎音效
        if (this.modules.audio) {
            this.modules.audio.playWelcomeSound();
        }
    }
    
    /**
     * 启动游戏循环
     */
    startGameLoop() {
        const gameLoop = () => {
            try {
                this.updateGame();
                this.renderGame();
            } catch (error) {
                console.error('❌ 游戏循环错误:', error);
            }
            
            requestAnimationFrame(gameLoop);
        };
        
        gameLoop();
    }
    
    /**
     * 更新游戏状态
     */
    updateGame() {
        if (!this.gameState.isPlaying) return;
        
        const now = Date.now();
        const deltaTime = now - this.gameState.lastUpdate;
        
        // 检查是否需要刷新状态
        this.checkForUpdates();
        
        // 更新角色状态
        this.updatePlayerStatus();
        
        // 更新时间
        this.gameState.lastUpdate = now;
    }
    
    /**
     * 渲染游戏
     */
    renderGame() {
        if (this.modules.ui) {
            this.modules.ui.render();
        }
        
        if (this.modules.profile) {
            this.modules.profile.render();
        }
    }
    
    /**
     * 检查更新
     */
    checkForUpdates() {
        fetch('/need_refresh')
            .then(response => response.json())
            .then(data => {
                if (data.refresh) {
                    this.refreshGameState();
                }
            })
            .catch(error => {
                if (this.isDebugMode) {
                    console.error('检查更新失败:', error);
                }
            });
    }
    
    /**
     * 刷新游戏状态
     */
    refreshGameState() {
        Promise.all([
            this.fetchGameStatus(),
            this.fetchGameLogs()
        ]).then(([status, logs]) => {
            this.updateGameState(status, logs);
        }).catch(error => {
            console.error('刷新游戏状态失败:', error);
        });
    }
    
    /**
     * 获取游戏状态
     */
    fetchGameStatus() {
        return fetch('/status').then(response => response.json());
    }
    
    /**
     * 获取游戏日志
     */
    fetchGameLogs() {
        return fetch('/log').then(response => response.json());
    }
    
    /**
     * 更新游戏状态
     */
    updateGameState(status, logs) {
        this.gameState.player = status.player;
        this.gameState.currentLocation = status.location;
        this.gameState.logs = logs.logs || [];
        
        // 通知模块更新
        if (this.modules.ui) {
            this.modules.ui.updateDisplay();
        }
        
        if (this.modules.profile) {
            this.modules.profile.updateProfile(status.player);
        }
    }
    
    /**
     * 更新玩家状态
     */
    updatePlayerStatus() {
        if (!this.gameState.player) return;

        // 这里可以添加实时状态更新逻辑
        // 例如：生命值恢复、灵力恢复等
    }

    /**
     * 连接事件流
     */
    connectEventStream() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        this.eventSource = new EventSource('/events');
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.player && this.modules.profile) {
                    this.modules.profile.updateProfile(data.player);
                }
            } catch (e) {
                console.error('事件流解析失败:', e);
            }
        };
        this.eventSource.onerror = (e) => {
            console.error('事件流连接失败:', e);
        };
    }
    
    /**
     * 启动游戏更新
     */
    startGameUpdates() {
        this.connectEventStream();
        this.gameUpdateInterval = setInterval(() => {
            this.checkForUpdates();
        }, 2000); // 每2秒检查一次更新
    }
    
    /**
     * 停止游戏更新
     */
    stopGameUpdates() {
        if (this.gameUpdateInterval) {
            clearInterval(this.gameUpdateInterval);
            this.gameUpdateInterval = null;
        }
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }
    
    /**
     * 处理键盘快捷键
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + Enter: 提交命令
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const input = document.querySelector('.command-input');
            if (input) {
                const form = input.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        }
        
        // F1: 显示帮助
        if (event.key === 'F1') {
            event.preventDefault();
            if (this.modules.modal) {
                this.modules.modal.showHelp();
            }
        }
        
        // F12: 切换开发者模式
        if (event.key === 'F12' && event.ctrlKey) {
            event.preventDefault();
            this.toggleDebugMode();
        }
        
        // Esc: 关闭模态框
        if (event.key === 'Escape') {
            if (this.modules.modal) {
                this.modules.modal.closeAll();
            }
        }
    }
    
    /**
     * 切换开发者模式
     */
    toggleDebugMode() {
        this.isDebugMode = !this.isDebugMode;
        
        if (this.isDebugMode) {
            this.enableDebugMode();
            sessionStorage.setItem('dev_mode', 'true');
            localStorage.setItem('dev', 'true');
        } else {
            this.disableDebugMode();
            sessionStorage.removeItem('dev_mode');
            localStorage.removeItem('dev');
        }
    }
    
    /**
     * 禁用开发者模式
     */
    disableDebugMode() {
        document.body.classList.remove('dev-mode');
        
        const console = document.querySelector('.dev-console');
        if (console) {
            console.remove();
        }
        
        if (window.XWE_DEBUG) {
            delete window.XWE_DEBUG;
        }
    }
    
    /**
     * 处理全局错误
     */
    handleGlobalError(event) {
        console.error('全局错误:', event.error);
        
        if (this.isDebugMode) {
            this.addDebugLog('ERROR', `全局错误: ${event.error.message}`);
        }
        
        // 显示用户友好的错误信息
        this.showErrorMessage('发生了一个错误，请刷新页面重试');
    }
    
    /**
     * 处理未捕获的Promise拒绝
     */
    handleUnhandledRejection(event) {
        console.error('未处理的Promise拒绝:', event.reason);
        
        if (this.isDebugMode) {
            this.addDebugLog('ERROR', `Promise拒绝: ${event.reason}`);
        }
    }
    
    /**
     * 窗口获得焦点
     */
    onWindowFocus() {
        if (this.gameState.isPlaying) {
            this.startGameUpdates();
        }
        
        if (this.modules.audio) {
            this.modules.audio.resumeAudio();
        }
    }
    
    /**
     * 窗口失去焦点
     */
    onWindowBlur() {
        this.stopGameUpdates();
        
        if (this.modules.audio) {
            this.modules.audio.pauseAudio();
        }
    }
    
    /**
     * 页面卸载前
     */
    onBeforeUnload() {
        if (this.settings.autoSave && this.gameState.isPlaying) {
            this.saveGame();
        }
        
        this.saveGameSettings();
    }
    
    /**
     * 保存游戏
     */
    async saveGame() {
        try {
            const response = await fetch('/save_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('游戏保存成功');
                this.showSuccessMessage('游戏保存成功');
            } else {
                console.error('游戏保存失败:', result.error);
                this.showErrorMessage('游戏保存失败: ' + result.error);
            }
        } catch (error) {
            console.error('保存游戏时发生错误:', error);
            this.showErrorMessage('保存游戏时发生错误');
        }
    }
    
    /**
     * 加载游戏
     */
    async loadGame() {
        try {
            const response = await fetch('/load_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('游戏加载成功');
                this.showSuccessMessage('游戏加载成功');
                this.refreshGameState();
            } else {
                console.error('游戏加载失败:', result.error);
                this.showErrorMessage('游戏加载失败: ' + result.error);
            }
        } catch (error) {
            console.error('加载游戏时发生错误:', error);
            this.showErrorMessage('加载游戏时发生错误');
        }
    }
    
    /**
     * 加载游戏设置
     */
    loadGameSettings() {
        const savedSettings = localStorage.getItem('xianxia_settings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                this.settings = { ...this.settings, ...settings };
            } catch (error) {
                console.error('加载设置失败:', error);
            }
        }
    }
    
    /**
     * 保存游戏设置
     */
    saveGameSettings() {
        try {
            localStorage.setItem('xianxia_settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('保存设置失败:', error);
        }
    }
    
    /**
     * 显示成功消息
     */
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    /**
     * 显示错误消息
     */
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    /**
     * 显示信息消息
     */
    showInfoMessage(message) {
        this.showMessage(message, 'info');
    }
    
    /**
     * 显示消息
     */
    showMessage(message, type = 'info') {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        
        // 添加到页面
        const container = document.querySelector('.game-output') || document.body;
        container.appendChild(messageElement);
        
        // 自动移除
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 5000);
        
        // 添加动画
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(-20px)';
        
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });
    }
    
    /**
     * 清除游戏日志
     */
    clearGameLogs() {
        this.gameState.logs = [];
        
        if (this.modules.ui) {
            this.modules.ui.clearDisplay();
        }
        
        console.log('游戏日志已清除');
    }
    
    /**
     * 导出游戏数据
     */
    exportGameData() {
        const data = {
            gameState: this.gameState,
            settings: this.settings,
            timestamp: Date.now()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `xianxia_save_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        console.log('游戏数据已导出');
    }
    
    /**
     * 导入游戏数据
     */
    importGameData(data) {
        try {
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            
            if (data.gameState) {
                this.gameState = { ...this.gameState, ...data.gameState };
            }
            
            if (data.settings) {
                this.settings = { ...this.settings, ...data.settings };
            }
            
            // 刷新显示
            this.refreshGameState();
            
            console.log('游戏数据已导入');
            this.showSuccessMessage('游戏数据导入成功');
        } catch (error) {
            console.error('导入游戏数据失败:', error);
            this.showErrorMessage('导入游戏数据失败');
        }
    }
    
    /**
     * 获取游戏统计信息
     */
    getGameStats() {
        return {
            uptime: Date.now() - this.gameState.lastUpdate,
            playerLevel: this.gameState.player?.attributes?.level || 0,
            currentLocation: this.gameState.currentLocation,
            logCount: this.gameState.logs.length,
            modules: Object.keys(this.modules).filter(key => this.modules[key] !== null)
        };
    }
    
    /**
     * 销毁控制器
     */
    destroy() {
        this.stopGameUpdates();
        
        // 清理模块
        Object.values(this.modules).forEach(module => {
            if (module && typeof module.destroy === 'function') {
                module.destroy();
            }
        });
        
        // 清理事件监听器
        document.removeEventListener('keydown', this.handleKeyboardShortcuts);
        window.removeEventListener('beforeunload', this.onBeforeUnload);
        
        console.log('🎮 游戏控制器已销毁');
    }
}

// 创建全局实例
window.XianxiaGame = new XianxiaGameController();

// 导出给其他模块使用
window.XianxiaGameController = XianxiaGameController;