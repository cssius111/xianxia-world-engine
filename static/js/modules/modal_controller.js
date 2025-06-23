/**
 * 修仙世界模拟器 - 模态框控制器
 * 负责各种模态框的管理和显示
 */

class XianxiaModalController {
    constructor(gameController) {
        this.game = gameController;
        this.activeModals = new Map();
        this.modalStack = [];
        this.defaultOptions = {
            backdrop: true,
            keyboard: true,
            focus: true,
            show: true
        };
        
        this.init();
    }
    
    /**
     * 初始化模态框控制器
     */
    init() {
        console.log('📋 模态框控制器初始化中...');
        
        // 设置全局事件监听
        this.setupGlobalEvents();
        
        // 预加载常用模态框
        this.preloadModals();
        
        console.log('✅ 模态框控制器初始化完成');
    }
    
    /**
     * 设置全局事件监听
     */
    setupGlobalEvents() {
        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });
        
        // 点击背景关闭模态框
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target.dataset.modalId);
            }
        });
    }
    
    /**
     * 预加载常用模态框
     */
    async preloadModals() {
        const commonModals = ['status', 'help', 'inventory'];
        
        for (const modalName of commonModals) {
            try {
                await this.loadModalContent(modalName);
            } catch (error) {
                console.warn(`预加载模态框失败: ${modalName}`, error);
            }
        }
    }
    
    /**
     * 显示模态框
     */
    async show(modalName, options = {}) {
        const modalOptions = { ...this.defaultOptions, ...options };
        
        try {
            // 加载模态框内容
            const content = await this.loadModalContent(modalName);
            
            // 创建模态框
            const modal = this.createModal(modalName, content, modalOptions);
            
            // 显示模态框
            this.displayModal(modal, modalOptions);
            
            // 记录活跃模态框
            this.activeModals.set(modalName, modal);
            this.modalStack.push(modalName);
            
            // 播放音效
            if (this.game.modules.audio) {
                this.game.modules.audio.playClickSound();
            }
            
            return modal;
            
        } catch (error) {
            console.error(`显示模态框失败: ${modalName}`, error);
            this.game.showErrorMessage('加载页面失败，请稍后重试');
        }
    }
    
    /**
     * 加载模态框内容
     */
    async loadModalContent(modalName) {
        // 检查缓存
        const cacheKey = `modal_${modalName}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) {
            return cached;
        }
        
        try {
            const response = await fetch(`/modal/${modalName}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            
            // 缓存内容
            this.setCache(cacheKey, content);
            
            return content;
            
        } catch (error) {
            console.error(`加载模态框内容失败: ${modalName}`, error);
            return this.getErrorModalContent(modalName, error.message);
        }
    }
    
    /**
     * 创建模态框
     */
    createModal(modalName, content, options) {
        const modalId = `modal-${modalName}-${Date.now()}`;
        
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.dataset.modalId = modalId;
        overlay.dataset.modalName = modalName;
        
        const modalContainer = document.createElement('div');
        modalContainer.className = 'modal-content';
        modalContainer.innerHTML = `
            <div class=\"modal-header\">
                <h3 class=\"modal-title\">${this.getModalTitle(modalName)}</h3>
                <button class=\"modal-close\" type=\"button\" aria-label=\"关闭\">&times;</button>
            </div>
            <div class=\"modal-body\">
                ${content}
            </div>
        `;
        
        overlay.appendChild(modalContainer);
        
        // 绑定关闭事件
        const closeBtn = modalContainer.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => this.closeModal(modalId));
        
        // 绑定内部事件
        this.bindModalEvents(modalContainer, modalName);
        
        return {
            id: modalId,
            name: modalName,
            element: overlay,
            container: modalContainer,
            options: options
        };
    }
    
    /**
     * 显示模态框
     */
    displayModal(modal, options) {
        document.body.appendChild(modal.element);
        
        // 触发显示动画
        requestAnimationFrame(() => {
            modal.element.classList.add('show');
        });
        
        // 聚焦到模态框
        if (options.focus) {
            this.focusModal(modal);
        }
        
        // 禁用背景滚动
        if (options.backdrop) {
            document.body.style.overflow = 'hidden';
        }
    }
    
    /**
     * 聚焦模态框
     */
    focusModal(modal) {
        // 聚焦到第一个可聚焦元素
        const focusableElements = modal.container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex=\"-1\"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
    
    /**
     * 关闭模态框
     */
    closeModal(modalId) {
        const modal = this.findModalById(modalId);
        if (!modal) return;
        
        // 播放关闭音效
        if (this.game.modules.audio) {
            this.game.modules.audio.playClickSound();
        }
        
        // 添加关闭动画
        modal.element.classList.add('hiding');
        
        setTimeout(() => {
            // 移除DOM元素
            if (modal.element.parentNode) {
                modal.element.parentNode.removeChild(modal.element);
            }
            
            // 从记录中移除
            this.activeModals.delete(modal.name);
            this.modalStack = this.modalStack.filter(name => name !== modal.name);
            
            // 恢复背景滚动
            if (this.modalStack.length === 0) {
                document.body.style.overflow = '';
            }
            
        }, 300); // 动画时长
    }
    
    /**
     * 关闭顶层模态框
     */
    closeTopModal() {
        if (this.modalStack.length > 0) {
            const topModalName = this.modalStack[this.modalStack.length - 1];
            const modal = this.activeModals.get(topModalName);
            if (modal) {
                this.closeModal(modal.id);
            }
        }
    }
    
    /**
     * 关闭所有模态框
     */
    closeAll() {
        const modals = Array.from(this.activeModals.values());
        modals.forEach(modal => this.closeModal(modal.id));
    }
    
    /**
     * 根据ID查找模态框
     */
    findModalById(modalId) {
        for (const modal of this.activeModals.values()) {
            if (modal.id === modalId) {
                return modal;
            }
        }
        return null;
    }
    
    /**
     * 获取模态框标题
     */
    getModalTitle(modalName) {
        const titleMap = {
            'status': '🧘 查看状态',
            'inventory': '🎒 查看背包',
            'cultivation': '⚡ 修炼系统',
            'achievement': '🏆 成就系统',
            'exploration': '🗺️ 进行探索',
            'map': '🗺️ 地图系统',
            'quest': '📋 当前任务',
            'save': '💾 保存加载',
            'load': '📂 加载游戏',
            'help': '❓ 帮助文档',
            'settings': '⚙️ 游戏设置',
            'exit': '🚪 退出游戏'
        };
        
        return titleMap[modalName] || modalName;
    }
    
    /**
     * 绑定模态框事件
     */
    bindModalEvents(container, modalName) {
        // 根据不同的模态框类型绑定特定事件
        switch (modalName) {
            case 'status':
                this.bindStatusModalEvents(container);
                break;
            case 'inventory':
                this.bindInventoryModalEvents(container);
                break;
            case 'cultivation':
                this.bindCultivationModalEvents(container);
                break;
            case 'achievement':
                this.bindAchievementModalEvents(container);
                break;
            case 'save':
                this.bindSaveModalEvents(container);
                break;
            case 'help':
                this.bindHelpModalEvents(container);
                break;
            default:
                this.bindCommonModalEvents(container);
        }
    }
    
    /**
     * 绑定状态模态框事件
     */
    bindStatusModalEvents(container) {
        // 属性详情切换
        const attributeTabs = container.querySelectorAll('.attribute-tab');
        attributeTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchAttributeTab(e.target, container);
            });
        });
        
        // 刷新按钮
        const refreshBtn = container.querySelector('.refresh-status');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshPlayerStatus(container);
            });
        }
    }
    
    /**
     * 绑定背包模态框事件
     */
    bindInventoryModalEvents(container) {
        // 物品点击事件
        const items = container.querySelectorAll('.inventory-item');
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleItemClick(e.target, container);
            });
        });
        
        // 物品分类切换
        const categoryTabs = container.querySelectorAll('.item-category');
        categoryTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchItemCategory(e.target, container);
            });
        });
    }
    
    /**
     * 绑定修炼模态框事件
     */
    bindCultivationModalEvents(container) {
        // 修炼按钮
        const cultivateBtn = container.querySelector('.cultivate-btn');
        if (cultivateBtn) {
            cultivateBtn.addEventListener('click', () => {
                this.handleCultivation(container);
            });
        }
        
        // 功法切换
        const techniques = container.querySelectorAll('.technique-item');
        techniques.forEach(technique => {
            technique.addEventListener('click', (e) => {
                this.selectTechnique(e.target, container);
            });
        });
    }
    
    /**
     * 绑定成就模态框事件
     */
    bindAchievementModalEvents(container) {
        // 成就分类切换
        const categoryTabs = container.querySelectorAll('.achievement-category');
        categoryTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchAchievementCategory(e.target, container);
            });
        });
        
        // 成就详情
        const achievements = container.querySelectorAll('.achievement-item');
        achievements.forEach(achievement => {
            achievement.addEventListener('click', (e) => {
                this.showAchievementDetail(e.target, container);
            });
        });
    }
    
    /**
     * 绑定保存模态框事件
     */
    bindSaveModalEvents(container) {
        // 保存游戏
        const saveBtn = container.querySelector('.save-game-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.handleSaveGame(container);
            });
        }
        
        // 加载游戏
        const loadBtn = container.querySelector('.load-game-btn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => {
                this.handleLoadGame(container);
            });
        }
        
        // 导出存档
        const exportBtn = container.querySelector('.export-save-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.handleExportSave();
            });
        }
        
        // 导入存档
        const importBtn = container.querySelector('.import-save-btn');
        if (importBtn) {
            importBtn.addEventListener('click', () => {
                this.handleImportSave();
            });
        }
    }
    
    /**
     * 绑定帮助模态框事件
     */
    bindHelpModalEvents(container) {
        // 帮助主题切换
        const topics = container.querySelectorAll('.help-topic');
        topics.forEach(topic => {
            topic.addEventListener('click', (e) => {
                this.switchHelpTopic(e.target, container);
            });
        });
        
        // 搜索功能
        const searchInput = container.querySelector('.help-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchHelp(e.target.value, container);
            });
        }
    }
    
    /**
     * 绑定通用模态框事件
     */
    bindCommonModalEvents(container) {
        // 通用按钮事件
        const buttons = container.querySelectorAll('button[data-action]');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleButtonAction(action, e.target, container);
            });
        });
        
        // 表单提交
        const forms = container.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e, container);
            });
        });
    }
    
    /**
     * 处理保存游戏
     */
    async handleSaveGame(container) {
        const saveBtn = container.querySelector('.save-game-btn');
        const originalText = saveBtn.textContent;
        
        saveBtn.textContent = '保存中...';
        saveBtn.disabled = true;
        
        try {
            await this.game.saveGame();
            this.showModalMessage(container, '游戏保存成功！', 'success');
        } catch (error) {
            this.showModalMessage(container, '保存失败：' + error.message, 'error');
        } finally {
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
        }
    }
    
    /**
     * 处理加载游戏
     */
    async handleLoadGame(container) {
        const loadBtn = container.querySelector('.load-game-btn');
        const originalText = loadBtn.textContent;
        
        loadBtn.textContent = '加载中...';
        loadBtn.disabled = true;
        
        try {
            await this.game.loadGame();
            this.showModalMessage(container, '游戏加载成功！', 'success');
            
            // 关闭模态框
            setTimeout(() => {
                this.closeAll();
            }, 1500);
        } catch (error) {
            this.showModalMessage(container, '加载失败：' + error.message, 'error');
        } finally {
            loadBtn.textContent = originalText;
            loadBtn.disabled = false;
        }
    }
    
    /**
     * 在模态框中显示消息
     */
    showModalMessage(container, message, type = 'info') {
        let messageContainer = container.querySelector('.modal-messages');
        
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.className = 'modal-messages';
            container.querySelector('.modal-body').prepend(messageContainer);
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        
        messageContainer.appendChild(messageElement);
        
        // 自动移除
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 5000);
    }
    
    /**
     * 刷新玩家状态
     */
    async refreshPlayerStatus(container) {
        try {
            await this.game.refreshGameState();
            this.showModalMessage(container, '状态已刷新', 'success');
            
            // 重新加载状态内容
            const newContent = await this.loadModalContent('status');
            const modalBody = container.querySelector('.modal-body');
            modalBody.innerHTML = newContent;
            
            // 重新绑定事件
            this.bindStatusModalEvents(container);
            
        } catch (error) {
            this.showModalMessage(container, '刷新失败：' + error.message, 'error');
        }
    }
    
    /**
     * 显示教程
     */
    async showTutorial() {
        const tutorialContent = `
            <div class=\"tutorial-content\">
                <h4>🎯 游戏操作指南</h4>
                <div class=\"tutorial-section\">
                    <h5>基本操作</h5>
                    <ul>
                        <li>在底部输入框中输入命令，按回车执行</li>
                        <li>点击左侧菜单可以快速访问各种功能</li>
                        <li>使用"帮助"命令查看所有可用命令</li>
                    </ul>
                </div>
                <div class=\"tutorial-section\">
                    <h5>常用命令</h5>
                    <ul>
                        <li><code>探索</code> - 探索当前区域</li>
                        <li><code>修炼</code> - 进行修炼提升境界</li>
                        <li><code>查看状态</code> - 查看角色详细信息</li>
                        <li><code>查看背包</code> - 管理物品和装备</li>
                    </ul>
                </div>
                <div class=\"tutorial-section\">
                    <h5>快捷键</h5>
                    <ul>
                        <li><kbd>F1</kbd> - 显示帮助</li>
                        <li><kbd>Esc</kbd> - 关闭模态框</li>
                        <li><kbd>Ctrl + Enter</kbd> - 提交命令</li>
                    </ul>
                </div>
            </div>
        `;
        
        const modal = this.createModal('tutorial', tutorialContent, {
            backdrop: true,
            keyboard: true
        });
        
        this.displayModal(modal, modal.options);
        this.activeModals.set('tutorial', modal);
        this.modalStack.push('tutorial');
    }
    
    /**
     * 显示确认对话框
     */
    async showConfirmDialog(message, title = '确认', options = {}) {
        return new Promise((resolve) => {
            const confirmContent = `
                <div class=\"confirm-dialog\">
                    <p class=\"confirm-message\">${message}</p>
                    <div class=\"confirm-buttons\">
                        <button class=\"button primary confirm-yes\">确定</button>
                        <button class=\"button secondary confirm-no\">取消</button>
                    </div>
                </div>
            `;
            
            const modal = this.createModal('confirm', confirmContent, {
                backdrop: false,
                keyboard: false
            });
            
            // 设置标题
            const titleElement = modal.container.querySelector('.modal-title');
            titleElement.textContent = title;
            
            // 绑定按钮事件
            const yesBtn = modal.container.querySelector('.confirm-yes');
            const noBtn = modal.container.querySelector('.confirm-no');
            
            yesBtn.addEventListener('click', () => {
                this.closeModal(modal.id);
                resolve(true);
            });
            
            noBtn.addEventListener('click', () => {
                this.closeModal(modal.id);
                resolve(false);
            });
            
            this.displayModal(modal, modal.options);
            this.activeModals.set('confirm', modal);
            this.modalStack.push('confirm');
        });
    }
    
    /**
     * 获取错误模态框内容
     */
    getErrorModalContent(modalName, errorMessage) {
        return `
            <div class=\"error-content\">
                <h4>❌ 加载失败</h4>
                <p>无法加载 ${modalName} 页面。</p>
                <p class=\"error-detail\">错误信息：${errorMessage}</p>
                <button class=\"button primary\" onclick=\"location.reload()\">刷新页面</button>
            </div>
        `;
    }
    
    /**
     * 缓存管理
     */
    getFromCache(key) {
        try {
            const cached = sessionStorage.getItem(key);
            if (cached) {
                const data = JSON.parse(cached);
                if (Date.now() - data.timestamp < 300000) { // 5分钟有效期
                    return data.content;
                }
            }
        } catch (error) {
            console.warn('读取缓存失败:', error);
        }
        return null;
    }
    
    setCache(key, content) {
        try {
            const data = {
                content: content,
                timestamp: Date.now()
            };
            sessionStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.warn('设置缓存失败:', error);
        }
    }
    
    /**
     * 清理缓存
     */
    clearCache() {
        const keys = Object.keys(sessionStorage);
        keys.forEach(key => {
            if (key.startsWith('modal_')) {
                sessionStorage.removeItem(key);
            }
        });
    }
    
    /**
     * 获取活跃模态框信息
     */
    getActiveModals() {
        return {
            count: this.activeModals.size,
            stack: [...this.modalStack],
            modals: Array.from(this.activeModals.keys())
        };
    }
    
    /**
     * 销毁模态框控制器
     */
    destroy() {
        // 关闭所有模态框
        this.closeAll();
        
        // 清理缓存
        this.clearCache();
        
        // 清理数据
        this.activeModals.clear();
        this.modalStack = [];
        
        // 恢复背景滚动
        document.body.style.overflow = '';
        
        console.log('📋 模态框控制器已销毁');
    }
}

// 导出供其他模块使用
window.XianxiaModalController = XianxiaModalController;