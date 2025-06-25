/**
 * 修仙世界模拟器 - UI控制器
 * 负责用户界面的交互和显示
 */

class XianxiaUIController {
    constructor(gameController) {
        this.game = gameController;
        this.elements = {};
        this.animations = new Map();
        this.updateQueue = [];
        
        this.init();
    }
    
    /**
     * 初始化UI控制器
     */
    init() {
        console.log('🎨 UI控制器初始化中...');
        
        // 缓存DOM元素
        this.cacheElements();
        
        // 设置事件监听器
        this.setupEventListeners();
        
        // 初始化UI状态
        this.initializeUI();
        
        // 启动动画系统
        this.startAnimationSystem();
        
        console.log('✅ UI控制器初始化完成');
    }
    
    /**
     * 缓存常用DOM元素
     */
    cacheElements() {
        this.elements = {
            // 主要容器
            gameContainer: document.querySelector('.game-container'),
            sidebar: document.querySelector('.sidebar'),
            mainContent: document.querySelector('.main-content'),
            gameOutput: document.querySelector('.game-output'),
            inputArea: document.querySelector('.input-area'),
            
            // 角色状态
            characterStatus: document.querySelector('.character-status'),
            characterName: document.querySelector('.character-name'),
            characterRealm: document.querySelector('.character-realm'),
            
            // 属性条
            healthBar: document.querySelector('[data-attribute="health"]'),
            manaBar: document.querySelector('[data-attribute="mana"]'),
            cultivationBar: document.querySelector('[data-attribute="cultivation"]'),
            
            // 功能菜单
            functionMenu: document.querySelector('.function-menu'),
            menuItems: document.querySelectorAll('.menu-item'),
            
            // 游戏日志
            gameLog: document.querySelector('.game-log'),
            
            // 输入表单
            inputForm: document.querySelector('.input-form'),
            commandInput: document.querySelector('.command-input'),
            submitButton: document.querySelector('.submit-button'),
            
            // 音频控制
            audioControls: document.querySelector('.audio-controls'),
            audioToggle: document.querySelector('.audio-toggle')
        };
        
        console.log('📋 DOM元素缓存完成');
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 命令输入表单
        if (this.elements.inputForm) {
            this.elements.inputForm.addEventListener('submit', (e) => this.handleCommandSubmit(e));
        }
        
        // 命令输入框
        if (this.elements.commandInput) {
            this.elements.commandInput.addEventListener('keydown', (e) => this.handleInputKeydown(e));
            this.elements.commandInput.addEventListener('input', (e) => this.handleInputChange(e));
        }
        
        // 功能菜单项
        this.elements.menuItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleMenuClick(e));
        });
        
        // 音频控制
        if (this.elements.audioToggle) {
            this.elements.audioToggle.addEventListener('click', (e) => this.handleAudioToggle(e));
        }
        
        // 窗口大小变化
        window.addEventListener('resize', () => this.handleWindowResize());
        
        // 滚动事件
        if (this.elements.gameOutput) {
            this.elements.gameOutput.addEventListener('scroll', (e) => this.handleOutputScroll(e));
        }
        
        console.log('🎯 事件监听器设置完成');
    }
    
    /**
     * 初始化UI状态
     */
    initializeUI() {
        // 设置初始样式
        this.applyInitialStyles();
        
        // 显示欢迎信息
        this.showWelcomeInfo();
        
        // 初始化动画效果
        this.initializeAnimations();
        
        // 设置响应式布局
        this.setupResponsiveLayout();
    }
    
    /**
     * 应用初始样式
     */
    applyInitialStyles() {
        // 添加淡入动画
        if (this.elements.gameContainer) {
            this.elements.gameContainer.classList.add('fade-in');
        }
        
        // 侧边栏滑入动画
        if (this.elements.sidebar) {
            this.elements.sidebar.classList.add('slide-in-left');
        }
        
        // 主内容区域滑入动画
        if (this.elements.mainContent) {
            this.elements.mainContent.classList.add('slide-in-right');
        }
    }
    
    /**
     * 显示欢迎信息
     */
    showWelcomeInfo() {
        const welcomeMessages = [
            '🏔️ 欢迎来到修仙世界...',
            '📜 在这里，你将开启一段传奇的修仙之旅',
            '⚔️ 修炼武功，探索世界，成就无上道途',
            '🎯 输入命令开始你的冒险吧！'
        ];
        
        let delay = 0;
        welcomeMessages.forEach((message, index) => {
            setTimeout(() => {
                this.addLogEntry(message, 'system-output special-event');
            }, delay);
            delay += 800;
        });
    }
    
    /**
     * 初始化动画
     */
    initializeAnimations() {
        // 水墨滴落效果
        this.startInkDropAnimation();
        
        // 属性条闪烁效果
        this.startAttributeBarAnimation();
        
        // 菜单项悬浮效果
        this.initializeMenuHoverEffects();
    }
    
    /**
     * 水墨滴落动画
     */
    startInkDropAnimation() {
        setInterval(() => {
            if (Math.random() < 0.1) { // 10%概率
                this.createInkDrop();
            }
        }, 2000);
    }
    
    /**
     * 创建水墨滴落
     */
    createInkDrop() {
        const drop = document.createElement('div');
        drop.className = 'ink-drop';
        drop.style.left = Math.random() * 100 + '%';
        drop.style.top = Math.random() * 100 + '%';
        
        if (this.elements.gameContainer) {
            this.elements.gameContainer.appendChild(drop);
            
            setTimeout(() => {
                if (drop.parentNode) {
                    drop.parentNode.removeChild(drop);
                }
            }, 2000);
        }
    }
    
    /**
     * 属性条动画
     */
    startAttributeBarAnimation() {
        const bars = document.querySelectorAll('.progress-fill');
        bars.forEach(bar => {
            // 添加微妙的脉冲效果
            bar.style.animation = 'shimmer 2s infinite';
        });
    }
    
    /**
     * 菜单悬浮效果
     */
    initializeMenuHoverEffects() {
        this.elements.menuItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                this.animateMenuItemHover(item, true);
            });
            
            item.addEventListener('mouseleave', () => {
                this.animateMenuItemHover(item, false);
            });
        });
    }
    
    /**
     * 菜单项悬浮动画
     */
    animateMenuItemHover(item, isHover) {
        if (isHover) {
            item.style.transform = 'translateY(-2px) scale(1.02)';
            item.style.boxShadow = '0 4px 16px rgba(212, 175, 55, 0.3)';
        } else {
            item.style.transform = 'translateY(0) scale(1)';
            item.style.boxShadow = '';
        }
    }
    
    /**
     * 设置响应式布局
     */
    setupResponsiveLayout() {
        const checkLayout = () => {
            const width = window.innerWidth;
            
            if (width <= 768) {
                document.body.classList.add('mobile-layout');
            } else {
                document.body.classList.remove('mobile-layout');
            }
            
            if (width <= 1024) {
                document.body.classList.add('tablet-layout');
            } else {
                document.body.classList.remove('tablet-layout');
            }
        };
        
        checkLayout();
        window.addEventListener('resize', checkLayout);
    }
    
    /**
     * 处理命令提交
     */
    async handleCommandSubmit(event) {
        event.preventDefault();
        
        const command = this.elements.commandInput.value.trim();
        if (!command) return;
        
        // 显示用户输入
        this.addLogEntry(`> ${command}`, 'player-input');
        
        // 清空输入框
        this.elements.commandInput.value = '';
        
        // 显示加载状态
        this.showLoadingState(true);
        
        try {
            // 发送命令到服务器
            const response = await fetch('/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 显示结果
                this.addLogEntry(result.result, 'system-output');
                
                // 播放音效
                if (this.game.modules.audio) {
                    this.game.modules.audio.playCommandSound();
                }
            } else {
                this.addLogEntry(`错误: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('发送命令失败:', error);
            this.addLogEntry('网络错误，请稍后重试', 'error');
        } finally {
            this.showLoadingState(false);
        }
    }
    
    /**
     * 处理输入框按键
     */
    handleInputKeydown(event) {
        // 上下箭头键切换历史命令
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            this.showPreviousCommand();
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            this.showNextCommand();
        }
        
        // Tab键自动补全
        if (event.key === 'Tab') {
            event.preventDefault();
            this.handleAutoComplete();
        }
    }
    
    /**
     * 处理输入变化
     */
    handleInputChange(event) {
        const value = event.target.value;
        
        // 显示输入提示
        this.showInputHints(value);
        
        // 更新字符计数
        this.updateCharacterCount(value);
    }
    
    /**
     * 显示输入提示
     */
    showInputHints(input) {
        const hints = this.getCommandHints(input);
        
        // 这里可以显示命令提示下拉框
        if (hints.length > 0) {
            // 实现命令提示UI
        }
    }
    
    /**
     * 获取命令提示
     */
    getCommandHints(input) {
        const commonCommands = [
            '探索', '修炼', '查看状态', '查看背包', '保存游戏', '帮助',
            '前往', '攻击', '使用', '购买', '出售', '对话', '休息'
        ];
        
        return commonCommands.filter(cmd => 
            cmd.toLowerCase().includes(input.toLowerCase())
        );
    }
    
    /**
     * 处理菜单点击
     */
    handleMenuClick(event) {
        event.preventDefault();
        
        const menuItem = event.currentTarget;
        const action = menuItem.dataset.action || menuItem.textContent.trim();
        
        // 添加点击动画
        this.animateMenuClick(menuItem);
        
        // 播放点击音效
        if (this.game.modules.audio) {
            this.game.modules.audio.playClickSound();
        }
        
        // 处理具体动作
        this.handleMenuAction(action);
    }
    
    /**
     * 菜单点击动画
     */
    animateMenuClick(item) {
        item.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            item.style.transform = '';
        }, 150);
    }
    
    /**
     * 处理菜单动作
     */
    handleMenuAction(action) {
        switch (action) {
            case '查看状态':
                this.openModal('status');
                break;
            case '查看背包':
                this.openModal('inventory');
                break;
            case '修炼系统':
                this.openModal('cultivation');
                break;
            case '成就系统':
                this.openModal('achievement');
                break;
            case '保存加载':
                this.openModal('save');
                break;
            case '帮助文档':
                this.openModal('help');
                break;
            case '地图系统':
                this.openModal('map');
                break;
            case '当前任务':
                this.openModal('quest');
                break;
            case '进行探索':
                this.executeCommand('探索');
                break;
            default:
                console.log('未知菜单动作:', action);
        }
    }
    
    /**
     * 打开模态框
     */
    async openModal(modalName) {
        if (this.game.modules.modal) {
            await this.game.modules.modal.show(modalName);
        }
    }
    
    /**
     * 执行命令
     */
    executeCommand(command) {
        this.elements.commandInput.value = command;
        
        // 触发提交事件
        const submitEvent = new Event('submit');
        this.elements.inputForm.dispatchEvent(submitEvent);
    }
    
    /**
     * 处理音频切换
     */
    handleAudioToggle(event) {
        if (this.game.modules.audio) {
            this.game.modules.audio.toggleAudio();
            
            // 更新按钮状态
            const button = event.currentTarget;
            const isEnabled = this.game.modules.audio.isEnabled();
            
            button.textContent = isEnabled ? '🔊' : '🔇';
            button.title = isEnabled ? '关闭音效' : '开启音效';
        }
    }
    
    /**
     * 处理窗口大小变化
     */
    handleWindowResize() {
        // 重新计算布局
        this.updateLayout();
        
        // 调整滚动位置
        this.adjustScrollPosition();
    }
    
    /**
     * 处理输出区域滚动
     */
    handleOutputScroll(event) {
        const element = event.target;
        const isAtBottom = element.scrollHeight - element.clientHeight <= element.scrollTop + 1;
        
        // 如果用户滚动到底部，自动滚动新内容
        if (isAtBottom) {
            this.autoScrollEnabled = true;
        } else {
            this.autoScrollEnabled = false;
        }
    }
    
    /**
     * 添加日志条目
     */
    addLogEntry(text, className = 'system-output') {
        if (!this.elements.gameLog) return;
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${className}`;
        entry.textContent = text;
        
        // 添加时间戳
        const timestamp = new Date().toLocaleTimeString();
        entry.dataset.timestamp = timestamp;
        
        this.elements.gameLog.appendChild(entry);
        
        // 自动滚动到底部
        if (this.autoScrollEnabled !== false) {
            this.scrollToBottom();
        }
        
        // 限制日志数量
        this.limitLogEntries();
        
        // 添加动画
        this.animateLogEntry(entry);
    }
    
    /**
     * 滚动到底部
     */
    scrollToBottom() {
        if (this.elements.gameOutput) {
            const scrollTop = this.elements.gameOutput.scrollHeight;
            
            this.elements.gameOutput.scrollTo({
                top: scrollTop,
                behavior: 'smooth'
            });
        }
    }
    
    /**
     * 限制日志条目数量
     */
    limitLogEntries() {
        const maxEntries = 200;
        const entries = this.elements.gameLog.querySelectorAll('.log-entry');
        
        if (entries.length > maxEntries) {
            const toRemove = entries.length - maxEntries;
            for (let i = 0; i < toRemove; i++) {
                entries[i].remove();
            }
        }
    }
    
    /**
     * 日志条目动画
     */
    animateLogEntry(entry) {
        entry.style.opacity = '0';
        entry.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            entry.style.transition = 'all 0.3s ease';
            entry.style.opacity = '1';
            entry.style.transform = 'translateY(0)';
        });
    }
    
    /**
     * 显示加载状态
     */
    showLoadingState(isLoading) {
        if (this.elements.submitButton) {
            if (isLoading) {
                this.elements.submitButton.innerHTML = '<div class="loading"></div>';
                this.elements.submitButton.disabled = true;
            } else {
                this.elements.submitButton.innerHTML = '发送';
                this.elements.submitButton.disabled = false;
            }
        }
        
        if (this.elements.commandInput) {
            this.elements.commandInput.disabled = isLoading;
        }
    }
    
    /**
     * 更新显示
     */
    updateDisplay() {
        // 更新角色状态
        this.updateCharacterDisplay();
        
        // 更新属性条
        this.updateAttributeBars();
        
        // 更新位置信息
        this.updateLocationDisplay();
        
        // 处理更新队列
        this.processUpdateQueue();
    }
    
    /**
     * 更新角色显示
     */
    updateCharacterDisplay() {
        const player = this.game.gameState.player;
        
        if (!player) return;
        
        // 更新角色名称
        if (this.elements.characterName) {
            this.elements.characterName.textContent = player.name || '无名侠客';
        }
        
        // 更新境界信息
        if (this.elements.characterRealm && player.attributes) {
            const realmText = `${player.attributes.realm_name || '炼气期'} (${player.attributes.realm_progress || 0}%)`;
            this.elements.characterRealm.textContent = realmText;
        }
    }
    
    /**
     * 更新属性条
     */
    updateAttributeBars() {
        const player = this.game.gameState.player;
        
        if (!player || !player.attributes) return;
        
        const attributes = [
            { name: 'health', current: 'current_health', max: 'max_health' },
            { name: 'mana', current: 'current_mana', max: 'max_mana' },
            { name: 'cultivation', current: 'cultivation_level', max: 'max_cultivation' }
        ];
        
        attributes.forEach(attr => {
            this.updateProgressBar(attr.name, 
                player.attributes[attr.current] || 0,
                player.attributes[attr.max] || 100
            );
        });
    }
    
    /**
     * 更新进度条
     */
    updateProgressBar(attributeName, current, max) {
        const bar = document.querySelector(`[data-attribute="${attributeName}"] .progress-fill`);
        const label = document.querySelector(`[data-attribute="${attributeName}"] .attribute-label`);
        
        if (bar) {
            const percentage = Math.min(100, Math.max(0, (current / max) * 100));
            bar.style.width = percentage + '%';
            
            // 根据百分比改变颜色
            if (percentage < 20) {
                bar.style.background = 'linear-gradient(90deg, #ff4444 0%, #ff6666 100%)';
            } else if (percentage < 50) {
                bar.style.background = 'linear-gradient(90deg, #ffaa00 0%, #ffcc44 100%)';
            } else {
                bar.style.background = 'linear-gradient(90deg, var(--brush-gold) 0%, #f4d03f 100%)';
            }
        }
        
        if (label) {
            const valueSpan = label.querySelector('.attribute-value') || label;
            valueSpan.textContent = `${current} / ${max}`;
        }
    }
    
    /**
     * 更新位置显示
     */
    updateLocationDisplay() {
        const location = this.game.gameState.currentLocation;
        
        if (location) {
            // 可以在某个地方显示当前位置
            console.log('当前位置:', location);
        }
    }
    
    /**
     * 处理更新队列
     */
    processUpdateQueue() {
        while (this.updateQueue.length > 0) {
            const update = this.updateQueue.shift();
            this.executeUpdate(update);
        }
    }
    
    /**
     * 执行更新
     */
    executeUpdate(update) {
        try {
            switch (update.type) {
                case 'log':
                    this.addLogEntry(update.message, update.className);
                    break;
                case 'status':
                    this.updateDisplay();
                    break;
                case 'animation':
                    this.playAnimation(update.animation);
                    break;
                default:
                    console.warn('未知更新类型:', update.type);
            }
        } catch (error) {
            console.error('执行更新失败:', error);
        }
    }
    
    /**
     * 清除显示
     */
    clearDisplay() {
        if (this.elements.gameLog) {
            this.elements.gameLog.innerHTML = '';
        }
    }
    
    /**
     * 更新布局
     */
    updateLayout() {
        // 重新计算容器高度
        if (this.elements.gameOutput) {
            const windowHeight = window.innerHeight;
            const otherElementsHeight = this.calculateOtherElementsHeight();
            const availableHeight = windowHeight - otherElementsHeight;
            
            this.elements.gameOutput.style.height = Math.max(200, availableHeight) + 'px';
        }
    }
    
    /**
     * 计算其他元素高度
     */
    calculateOtherElementsHeight() {
        let height = 0;
        
        if (this.elements.inputArea) {
            height += this.elements.inputArea.offsetHeight;
        }
        
        // 添加其他固定元素的高度
        height += 40; // 边距等
        
        return height;
    }
    
    /**
     * 调整滚动位置
     */
    adjustScrollPosition() {
        if (this.autoScrollEnabled !== false) {
            this.scrollToBottom();
        }
    }
    
    /**
     * 启动动画系统
     */
    startAnimationSystem() {
        this.animationLoop();
    }
    
    /**
     * 动画循环
     */
    animationLoop() {
        // 处理动画队列
        this.animations.forEach((animation, id) => {
            if (animation.update) {
                animation.update();
            }
            
            if (animation.finished) {
                this.animations.delete(id);
            }
        });
        
        requestAnimationFrame(() => this.animationLoop());
    }
    
    /**
     * 播放动画
     */
    playAnimation(animationData) {
        const id = Date.now() + Math.random();
        this.animations.set(id, animationData);
    }
    
    /**
     * 渲染
     */
    render() {
        // 这里可以添加需要每帧更新的UI元素
        this.updateTimeSensitiveElements();
    }
    
    /**
     * 更新时间敏感元素
     */
    updateTimeSensitiveElements() {
        // 更新时间显示、动画状态等
    }
    
    /**
     * 销毁UI控制器
     */
    destroy() {
        // 清理事件监听器
        this.elements.menuItems.forEach(item => {
            item.removeEventListener('click', this.handleMenuClick);
        });
        
        // 清理动画
        this.animations.clear();
        
        console.log('🎨 UI控制器已销毁');
    }
}

// 导出供其他模块使用
window.XianxiaUIController = XianxiaUIController;