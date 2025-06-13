/**
 * 世界观系统模块
 * 处理游戏世界观、剧情介绍的展示和交互
 */

const LoreSystem = (function() {
    'use strict';
    
    // 私有变量
    let currentPages = [];
    let currentPageIndex = 0;
    let isLoading = false;
    let onCompleteCallback = null;
    
    // 配置
    const CONFIG = {
        fadeInDuration: 300,
        fadeOutDuration: 200,
        pageTransitionDuration: 150
    };
    
    /**
     * 初始化Lore系统
     */
    function init() {
        // 确保marked.js已加载
        if (typeof marked === 'undefined') {
            console.error('LoreSystem: marked.js 未加载');
            loadMarkedJS();
        }
        
        // 绑定键盘事件
        document.addEventListener('keydown', handleKeyPress);
    }
    
    /**
     * 动态加载marked.js
     */
    function loadMarkedJS() {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
        script.onload = () => {
            console.log('marked.js 已加载');
        };
        document.head.appendChild(script);
    }
    
    /**
     * 处理键盘事件
     */
    function handleKeyPress(event) {
        const modal = document.getElementById('loreModal');
        if (!modal || modal.style.display === 'none') return;
        
        switch(event.key) {
            case 'ArrowLeft':
                previousPage();
                break;
            case 'ArrowRight':
                nextPage();
                break;
            case 'Escape':
                skipLore();
                break;
        }
    }
    
    /**
     * 显示世界观介绍
     * @param {Function} onComplete - 完成后的回调函数
     */
    async function showLore(onComplete) {
        if (isLoading) return;
        
        onCompleteCallback = onComplete;
        isLoading = true;
        
        try {
            // 获取世界观内容
            const response = await fetch('/api/lore');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || '加载世界观失败');
            }
            
            // 解析内容为页面
            parseContent(data.content);
            
            // 显示模态框
            const modal = document.getElementById('loreModal');
            modal.style.display = 'flex';
            
            // 渲染第一页
            currentPageIndex = 0;
            renderCurrentPage();
            
        } catch (error) {
            console.error('加载世界观失败:', error);
            alert('加载世界观内容失败，请刷新页面重试');
        } finally {
            isLoading = false;
        }
    }
    
    /**
     * 解析Markdown内容为页面
     */
    function parseContent(markdown) {
        // 按 --- 分割章节
        const sections = markdown.split(/\n---\n/);
        
        currentPages = sections.map(section => {
            // 清理空白行
            return section.trim();
        }).filter(page => page.length > 0);
        
        console.log(`世界观内容已解析为 ${currentPages.length} 页`);
    }
    
    /**
     * 渲染当前页面
     */
    function renderCurrentPage() {
        const contentEl = document.getElementById('loreContent');
        const progressEl = document.getElementById('loreProgress');
        const prevBtn = document.getElementById('prevLore');
        const nextBtn = document.getElementById('nextLore');
        
        // 更新内容
        const currentContent = currentPages[currentPageIndex];
        
        // 渲染Markdown
        if (typeof marked !== 'undefined') {
            contentEl.innerHTML = marked.parse(currentContent);
        } else {
            // 如果marked未加载，显示原始文本
            contentEl.innerHTML = `<pre style="white-space: pre-wrap;">${currentContent}</pre>`;
        }
        
        // 添加淡入动画
        contentEl.style.opacity = '0';
        setTimeout(() => {
            contentEl.style.transition = 'opacity 0.3s ease';
            contentEl.style.opacity = '1';
        }, 10);
        
        // 更新进度
        progressEl.textContent = `第 ${currentPageIndex + 1} 页 / 共 ${currentPages.length} 页`;
        
        // 更新按钮状态
        prevBtn.disabled = currentPageIndex === 0;
        
        // 最后一页时，"下一页"按钮改为"开始游戏"
        if (currentPageIndex === currentPages.length - 1) {
            nextBtn.textContent = '开始游戏';
            nextBtn.classList.add('lore-btn-start');
        } else {
            nextBtn.textContent = '下一页';
            nextBtn.classList.remove('lore-btn-start');
        }
        
        // 滚动到顶部
        document.querySelector('.lore-body').scrollTop = 0;
    }
    
    /**
     * 上一页
     */
    function previousPage() {
        if (currentPageIndex > 0) {
            currentPageIndex--;
            renderCurrentPage();
        }
    }
    
    /**
     * 下一页
     */
    function nextPage() {
        if (currentPageIndex < currentPages.length - 1) {
            currentPageIndex++;
            renderCurrentPage();
        } else {
            // 最后一页，关闭世界观
            closeLore();
        }
    }
    
    /**
     * 跳过引导
     */
    function skipLore() {
        if (confirm('确定要跳过世界观介绍吗？\n你可以在游戏中通过"帮助"命令随时查看。')) {
            closeLore();
        }
    }
    
    /**
     * 关闭世界观模态框
     */
    function closeLore() {
        const modal = document.getElementById('loreModal');
        
        // 淡出动画
        modal.style.transition = `opacity ${CONFIG.fadeOutDuration}ms ease`;
        modal.style.opacity = '0';
        
        setTimeout(() => {
            modal.style.display = 'none';
            modal.style.opacity = '1';
            
            // 执行回调
            if (typeof onCompleteCallback === 'function') {
                onCompleteCallback();
            }
        }, CONFIG.fadeOutDuration);
    }
    
    /**
     * 显示特定的剧情文件
     * @param {string} filename - 剧情文件名
     */
    async function showLoreFile(filename) {
        if (isLoading) return;
        
        isLoading = true;
        
        try {
            const response = await fetch(`/api/lore/${filename}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || '加载剧情失败');
            }
            
            // 解析并显示
            parseContent(data.content);
            
            const modal = document.getElementById('loreModal');
            modal.style.display = 'flex';
            
            currentPageIndex = 0;
            renderCurrentPage();
            
        } catch (error) {
            console.error('加载剧情失败:', error);
            alert('加载剧情内容失败');
        } finally {
            isLoading = false;
        }
    }
    
    /**
     * 检查是否是新玩家
     */
    function isNewPlayer() {
        // 检查本地存储
        const hasSeenIntro = localStorage.getItem('xianxia_seen_intro');
        return !hasSeenIntro;
    }
    
    /**
     * 标记已看过介绍
     */
    function markIntroSeen() {
        localStorage.setItem('xianxia_seen_intro', 'true');
    }
    
    // 公开API
    return {
        init,
        showLore,
        showLoreFile,
        previousPage,
        nextPage,
        skipLore,
        closeLore,
        isNewPlayer,
        markIntroSeen
    };
})();

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', LoreSystem.init);
} else {
    LoreSystem.init();
}

// 导出到全局（兼容性）
window.LoreSystem = LoreSystem;