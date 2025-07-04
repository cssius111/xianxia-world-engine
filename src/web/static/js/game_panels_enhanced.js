/**
 * 游戏面板系统 - 增强版
 * 集成所有修复的API接口
 */
const GamePanels = {
    currentPanel: null,

    /**
     * 显示面板
     */
    showPanel(panelId) {
        // 关闭当前面板
        if (this.currentPanel) {
            document.getElementById(this.currentPanel).style.display = 'none';
        }

        // 显示遮罩和新面板
        document.getElementById('panelOverlay').style.display = 'flex';
        document.getElementById(panelId).style.display = 'flex';
        this.currentPanel = panelId;
        
        // 保存当前打开的面板到sessionStorage
        try {
            sessionStorage.setItem('sidebar:last', panelId);
        } catch (e) {
            console.warn('无法保存面板状态:', e);
        }

        // 加载面板数据
        this.loadPanelData(panelId);
    },

    /**
     * 关闭面板
     */
    closePanel(panelId) {
        document.getElementById(panelId).style.display = 'none';
        document.getElementById('panelOverlay').style.display = 'none';
        this.currentPanel = null;
    },

    /**
     * 点击遮罩关闭面板
     */
    closeCurrentPanel(event) {
        if (event.target.id === 'panelOverlay') {
            if (this.currentPanel) {
                this.closePanel(this.currentPanel);
            }
        }
    },

    refreshCurrentPanel() {
        if (this.currentPanel) {
            this.loadPanelData(this.currentPanel);
        }
    },

    /**
     * 加载面板数据
     */
    loadPanelData(panelId) {
        switch(panelId) {
            case 'statusPanel':
                this.loadStatusData();
                break;
            case 'inventoryPanel':
                this.loadInventoryData();
                break;
            case 'cultivationPanel':
                this.loadCultivationData();
                break;
            case 'achievementsPanel':
                this.loadAchievementsData();
                break;
            case 'mapPanel':
                this.loadMapData();
                break;
            case 'questsPanel':
                this.loadQuestsData();
                break;
            case 'intelPanel':
                this.loadIntelData();
                break;
        }
    },

    // 各功能入口
    showStatus() { this.showPanel('statusPanel'); },
    showInventory() { this.showPanel('inventoryPanel'); },
    showCultivation() { this.showPanel('cultivationPanel'); },
    showAchievements() { this.showPanel('achievementsPanel'); },
    showExplore() { this.showPanel('explorePanel'); },
    showMap() { this.showPanel('mapPanel'); },
    showQuests() { this.showPanel('questsPanel'); },
    showIntel() { this.showPanel('intelPanel'); },
    showSaveLoad() { this.showPanel('saveLoadPanel'); },
    showHelp() { this.showPanel('helpPanel'); },

    /**
     * 加载详细状态数据
     */
    async loadStatusData() {
        try {
            // 使用新的详细状态API
            const response = await fetch('/api/player/stats/detailed');
            
            if (response.ok) {
                const result = await response.json();
                const data = result.data;
                
                // 更新基础信息
                document.getElementById('status-name').textContent = data.basic_info.name || '-';
                document.getElementById('status-realm').textContent = 
                    `${data.basic_info.realm} ${data.basic_info.realm_level}层` || '-';
                document.getElementById('status-cultivation').textContent = 
                    `${data.cultivation.cultivation_level}/${data.cultivation.max_cultivation}`;
                document.getElementById('status-faction').textContent = data.social.faction || '散修';
                
                // 更新属性
                document.getElementById('status-constitution').textContent = data.attributes.constitution ?? '5';
                document.getElementById('status-comprehension').textContent = data.attributes.comprehension ?? '5';
                document.getElementById('status-spirit').textContent = data.attributes.spirit ?? '5';
                document.getElementById('status-luck').textContent = data.attributes.luck ?? '5';
                
                // 更新资源
                document.getElementById('status-gold').textContent = data.resources.gold || '0';
                document.getElementById('status-lifespan').textContent = 
                    `${data.combat_stats.current_health}/${data.combat_stats.max_health}`;
                document.getElementById('status-reputation').textContent = data.social.reputation || '0';
                
                console.log('✅ 状态数据加载成功');
            } else {
                // 回退到原有API
                await this.loadStatusDataFallback();
            }
        } catch (error) {
            console.error('加载详细状态数据失败:', error);
            await this.loadStatusDataFallback();
        }
    },

    /**
     * 回退的状态数据加载方法
     */
    async loadStatusDataFallback() {
        try {
            const response = await fetch('/status');
            const data = await response.json();

            if (data.player) {
                const player = data.player;
                document.getElementById('status-name').textContent = player.name || '-';
                document.getElementById('status-realm').textContent = player.attributes?.realm_name || '-';
                document.getElementById('status-cultivation').textContent = 
                    `${player.attributes?.cultivation_level || 0}/${player.attributes?.max_cultivation || 100}`;
                document.getElementById('status-faction').textContent = player.faction || '散修';
                
                const attrs = player.attributes || {};
                document.getElementById('status-constitution').textContent = attrs.constitution ?? '5';
                document.getElementById('status-comprehension').textContent = attrs.comprehension ?? '5';
                document.getElementById('status-spirit').textContent = attrs.willpower ?? attrs.spirit ?? '5';
                document.getElementById('status-luck').textContent = attrs.luck ?? '5';
                document.getElementById('status-gold').textContent = data.gold || '0';
                document.getElementById('status-lifespan').textContent = player.lifespan || '100/100';
                document.getElementById('status-reputation').textContent = player.reputation || '0';
            }
        } catch (error) {
            console.error('加载状态失败:', error);
        }
    },

    /**
     * 加载背包数据 (保持原有逻辑)
     */
    async loadInventoryData() {
        try {
            const resp = await fetch('/status');
            if (!resp.ok) {
                console.error('加载背包接口失败:', resp.status);
                return;
            }
            const data = await resp.json();
            const inventory = data.inventory || { items: [] };

            const grid = document.getElementById('inventoryGrid');
            grid.innerHTML = '';

            let items = inventory.items || [];
            if (!Array.isArray(items)) {
                items = Object.values(items);
            }

            const totalSlots = 24;
            for (let i = 0; i < totalSlots; i++) {
                const slot = document.createElement('div');
                slot.className = 'inventory-slot';
                if (i < items.length) {
                    const item = items[i] || {};
                    const name = item.name || item.id || '未知物品';
                    const qty = item.quantity ?? item.qty ?? item.count ?? 1;
                    slot.innerHTML = `<span>${name}</span><span class="item-qty">x${qty}</span>`;
                    slot.onclick = () => this.showItemInfo({ name, desc: name, count: qty });
                }
                grid.appendChild(slot);
            }
        } catch (e) {
            console.error('加载背包失败:', e);
        }
    },

    /**
     * 加载修炼数据 - 使用新API
     */
    async loadCultivationData() {
        try {
            const response = await fetch('/api/cultivation/status');
            
            if (response.ok) {
                const data = await response.json();
                
                // 如果有realm和progress字段（新API格式）
                if (data.realm !== undefined && data.progress !== undefined) {
                    // 显示境界信息
                    document.getElementById('currentTechnique').textContent = data.realm;
                    document.getElementById('techniqueProgress').textContent = 
                        `进度(${data.progress}%)`;
                    
                    // 更新修炼设置
                    document.getElementById('maxCultivationTime').textContent = data.max_hours || '8';
                    
                    // 显示天劫信息（如果有）
                    if (data.next_tribulation) {
                        document.getElementById('cultivationWarning').textContent = 
                            `警告：即将面临${data.next_tribulation.name || '天劫'}`;
                    } else {
                        document.getElementById('cultivationWarning').textContent = data.warning || '';
                    }
                }
                // 如果有完整的功法信息（兼容旧格式）
                else if (data.current_technique) {
                    // 更新当前功法
                    document.getElementById('currentTechnique').textContent = data.current_technique;
                    document.getElementById('techniqueProgress').textContent = 
                        `${data.technique_level || ''}(${data.progress || 0}%)`;

                    // 更新功法列表
                    const list = document.getElementById('techniqueList');
                    list.innerHTML = '';

                    if (data.techniques) {
                        data.techniques.forEach(tech => {
                            const item = document.createElement('div');
                            item.className = 'technique-item';
                            item.innerHTML = `
                                <span style="color: ${tech.color || '#666'}">${tech.name}</span> 
                                - ${tech.level}
                            `;
                            list.appendChild(item);
                        });
                    }

                    // 更新修炼设置
                    document.getElementById('maxCultivationTime').textContent = data.max_hours || '8';
                    document.getElementById('cultivationWarning').textContent = data.warning || '';
                }
                
                console.log('✅ 修炼数据加载成功');
            } else {
                // 回退到原有逻辑
                this.loadCultivationDataFallback();
            }
        } catch (error) {
            console.error('加载修炼数据失败:', error);
            this.loadCultivationDataFallback();
        }
    },

    /**
     * 回退的修炼数据加载
     */
    loadCultivationDataFallback() {
        // 当前功法
        document.getElementById('currentTechnique').textContent = '青云诀';
        document.getElementById('techniqueProgress').textContent = '入门(25%)';

        // 功法列表
        const techniques = [
            { name: '青云诀', level: '黄阶下品', color: '#4CAF50' },
            { name: '烈火诀', level: '黄阶中品', color: '#666' },
            { name: '寒冰诀', level: '黄阶中品', color: '#666' }
        ];

        const list = document.getElementById('techniqueList');
        list.innerHTML = '';

        techniques.forEach(tech => {
            const item = document.createElement('div');
            item.className = 'technique-item';
            item.innerHTML = `<span style="color: ${tech.color}">${tech.name}</span> - ${tech.level}`;
            list.appendChild(item);
        });

        // 修炼限制
        document.getElementById('maxCultivationTime').textContent = '8';
        document.getElementById('cultivationWarning').textContent = '注意：当前体力只能支撑8小时修炼';
    },

    /**
     * 加载成就数据 - 使用新API
     */
    async loadAchievementsData() {
        try {
            const response = await fetch('/api/achievements');
            
            if (response.ok) {
                const result = await response.json();
                const achievements = result.achievements;

                const tbody = document.getElementById('achievementList');
                tbody.innerHTML = '';

                achievements.forEach(ach => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="color: ${ach.unlocked ? '#4CAF50' : '#666'}">${ach.unlocked ? ach.name : '???'}</td>
                        <td>${ach.unlocked ? ach.description : '未解锁'}</td>
                        <td>${ach.unlocked ? '✓' : '✗'}</td>
                    `;
                    if (ach.unlocked) {
                        tr.title = `解锁时间: ${ach.unlock_time}\n奖励: ${ach.reward}`;
                    }
                    tbody.appendChild(tr);
                });

                console.log(`✅ 成就数据加载成功 (${result.unlocked}/${result.total})`);
            } else {
                // 回退到原有逻辑
                this.loadAchievementsDataFallback();
            }
        } catch (error) {
            console.error('加载成就数据失败:', error);
            this.loadAchievementsDataFallback();
        }
    },

    /**
     * 回退的成就数据加载
     */
    loadAchievementsDataFallback() {
        const achievements = [
            { name: '初入仙门', desc: '踏上修仙之路', unlocked: true },
            { name: '筑基成功', desc: '突破至筑基期', unlocked: false },
            { name: '丹成九转', desc: '炼制出九转金丹', unlocked: false },
            { name: '剑心通明', desc: '领悟剑道真意', unlocked: false }
        ];

        const tbody = document.getElementById('achievementList');
        tbody.innerHTML = '';

        achievements.forEach(ach => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${ach.unlocked ? ach.name : '???'}</td>
                <td>${ach.unlocked ? ach.desc : '未解锁'}</td>
                <td>${ach.unlocked ? '✓' : '✗'}</td>
            `;
            tbody.appendChild(tr);
        });
    },

    /**
     * 加载地图数据 - 使用新API
     */
    async loadMapData() {
        try {
            const response = await fetch('/api/map');
            
            if (response.ok) {
                const result = await response.json();
                const mapData = result.data;

                const mapContainer = document.getElementById('mapContainer');
                mapContainer.innerHTML = '';

                mapData.regions.forEach(region => {
                    const regionDiv = document.createElement('div');
                    regionDiv.className = 'map-region';
                    regionDiv.innerHTML = `<h4>${region.name}</h4><p>${region.description}</p>`;

                    const locationList = document.createElement('ul');
                    region.locations.forEach(location => {
                        const li = document.createElement('li');
                        const statusIcon = location.discovered ? '🗺️' : '❓';
                        const accessStyle = location.accessible ? 'color: #4CAF50; cursor: pointer;' : 'color: #666;';
                        
                        li.innerHTML = `
                            <span style="${accessStyle}" onclick="${location.accessible ? `GamePanels.travelTo('${location.name}')` : ''}"">
                                ${statusIcon} ${location.name}
                            </span> - ${location.description}
                        `;
                        locationList.appendChild(li);
                    });

                    regionDiv.appendChild(locationList);
                    mapContainer.appendChild(regionDiv);
                });

                console.log('✅ 地图数据加载成功');
            } else {
                // 回退到原有逻辑
                this.loadMapDataFallback();
            }
        } catch (error) {
            console.error('加载地图数据失败:', error);
            this.loadMapDataFallback();
        }
    },

    /**
     * 回退的地图数据加载
     */
    loadMapDataFallback() {
        const mapContainer = document.getElementById('mapContainer');
        mapContainer.innerHTML = `
            <div class="map-region">
                <h4>青云山脉</h4>
                <ul>
                    <li><a href="#" onclick="GamePanels.travelTo('青云城')">青云城</a> - 繁华的修真城市</li>
                    <li><a href="#" onclick="GamePanels.travelTo('青云峰')">青云峰</a> - 青云宗山门</li>
                    <li><a href="#" onclick="GamePanels.travelTo('灵兽森林')">灵兽森林<span style="color: #FFA500">(新)</span></a> - 危险的森林</li>
                </ul>
            </div>
        `;
    },

    /**
     * 加载任务数据 - 使用新API
     */
    async loadQuestsData() {
        try {
            const response = await fetch('/api/quests');
            
            if (response.ok) {
                const result = await response.json();
                const quests = result.quests;

                const list = document.getElementById('questList');
                list.innerHTML = '';

                quests.forEach(quest => {
                    const item = document.createElement('div');
                    item.className = 'quest-item';
                    
                    const statusColor = quest.status === 'active' ? '#4CAF50' : 
                                       quest.status === 'completed' ? '#2196F3' : '#FFA500';
                    
                    item.innerHTML = `
                        <h5 style="color: ${statusColor}">${quest.name}</h5>
                        <p>${quest.description}</p>
                        <p style="color: #888">状态：${this.getQuestStatusText(quest.status)}</p>
                        <p style="color: #888">进度：${quest.progress}/${quest.max_progress}</p>
                        <div class="quest-objectives">
                            ${quest.objectives.map(obj => 
                                `<p style="color: ${obj.completed ? '#4CAF50' : '#666'}">
                                    ${obj.completed ? '✓' : '○'} ${obj.text}
                                </p>`
                            ).join('')}
                        </div>
                    `;
                    
                    if (quest.status === 'active') {
                        item.style.borderLeft = '3px solid #4CAF50';
                    }
                    
                    list.appendChild(item);
                });

                console.log(`✅ 任务数据加载成功 (活跃: ${result.active_count}, 可用: ${result.available_count})`);
            } else {
                // 回退到原有逻辑
                this.loadQuestsDataFallback();
            }
        } catch (error) {
            console.error('加载任务数据失败:', error);
            this.loadQuestsDataFallback();
        }
    },

    /**
     * 回退的任务数据加载
     */
    loadQuestsDataFallback() {
        const quests = [
            { name: '初入青云', desc: '前往青云城了解情况', progress: '进行中' },
            { name: '寻找机缘', desc: '探索周围区域，寻找修炼资源', progress: '未开始' }
        ];

        const list = document.getElementById('questList');
        list.innerHTML = '';

        quests.forEach(quest => {
            const item = document.createElement('div');
            item.className = 'quest-item';
            item.innerHTML = `
                <h5>${quest.name}</h5>
                <p>${quest.desc}</p>
                <p style="color: #888">状态：${quest.progress}</p>
            `;
            list.appendChild(item);
        });
    },

    /**
     * 加载情报数据 - 使用新API
     */
    async loadIntelData(tab = 'world') {
        try {
            const response = await fetch('/api/intel');
            
            if (response.ok) {
                const result = await response.json();
                const intelData = result.data;
                
                const list = document.getElementById('intelList');
                list.innerHTML = '';
                
                const items = tab === 'world' ? intelData.global : intelData.personal;
                
                items.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'intel-item';
                    
                    const importanceColor = item.importance === 'high' ? '#f44336' : 
                                           item.importance === 'medium' ? '#FF9800' : '#4CAF50';
                    
                    div.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h6 style="margin: 0; color: ${importanceColor}">${item.title}</h6>
                            <small style="color: #888">${item.time}</small>
                        </div>
                        <p style="margin: 5px 0; font-size: 14px;">${item.content}</p>
                        <small style="color: #666">来源: ${item.source}</small>
                    `;
                    
                    if (item.interactable_task_id) {
                        div.style.cursor = 'pointer';
                        div.onclick = () => this.showIntelDetail(item);
                    }
                    
                    list.appendChild(div);
                });

                // 更新标签状态
                document.getElementById('intelTabWorld').classList.toggle('active', tab === 'world');
                document.getElementById('intelTabPersonal').classList.toggle('active', tab === 'personal');
                
                console.log(`✅ 情报数据加载成功 (${tab})`);
            } else {
                // 回退到原有逻辑
                this.loadIntelDataFallback(tab);
            }
        } catch (error) {
            console.error('加载情报数据失败:', error);
            this.loadIntelDataFallback(tab);
        }
    },

    /**
     * 回退的情报数据加载
     */
    loadIntelDataFallback(tab = 'world') {
        const list = document.getElementById('intelList');
        list.innerHTML = '<p style="color: #888; text-align: center; padding: 20px;">情报系统开发中...</p>';
        
        document.getElementById('intelTabWorld').classList.toggle('active', tab === 'world');
        document.getElementById('intelTabPersonal').classList.toggle('active', tab === 'personal');
    },

    /**
     * 辅助方法
     */
    getQuestStatusText(status) {
        const statusMap = {
            'active': '进行中',
            'completed': '已完成',
            'available': '可接取',
            'failed': '已失败'
        };
        return statusMap[status] || status;
    },

    switchIntelTab(tab) {
        this.loadIntelData(tab);
    },

    showIntelDetail(item) {
        alert(item.content);
        if (item.interactable_task_id) {
            this.showQuests();
        }
    },

    showItemInfo(item) {
        document.getElementById('itemInfo').style.display = 'block';
        document.getElementById('itemName').textContent = item.name;
        document.getElementById('itemDesc').textContent = item.desc;
        document.getElementById('itemCount').textContent = item.count;
    },

    /**
     * 开始修炼 - 使用新API
     */
    async startCultivation() {
        const hours = document.getElementById('cultivationHours').value;
        
        try {
            const response = await fetch('/api/cultivation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hours: parseInt(hours) })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 显示修炼结果
                if (window.NarrativeLog) {
                    window.NarrativeLog.addResult(result.result);
                }
                this.closePanel('cultivationPanel');
                
                // 刷新状态
                if (window.GameUI && window.GameUI.refreshStatus) {
                    window.GameUI.refreshStatus();
                }
            } else {
                alert('修炼失败：' + result.error);
            }
        } catch (error) {
            console.error('开始修炼失败:', error);
            // 回退到原有方法
            if (typeof GameUI !== 'undefined' && GameUI.sendCommand) {
                GameUI.sendCommand(`修炼 ${hours}小时`);
            }
            this.closePanel('cultivationPanel');
        }
    },

    /**
     * 进行探索 (保持原有逻辑)
     */
    async doExplore() {
        const result = document.getElementById('exploreResult');
        result.style.display = 'block';
        result.innerHTML = '<p>正在探索中...</p>';

        try {
            const response = await fetch('/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: '探索', command: '探索' })
            });
            const data = await response.json();
            result.innerHTML = `<p>${data.result || '探索失败'}</p>`;

            if (data.bag_updated) {
                this.loadInventoryData();
            }
        } catch (e) {
            console.error('探索失败:', e);
            result.innerHTML = '<p>探索失败，请稍后再试。</p>';
        }
    },

    /**
     * 前往地点
     */
    travelTo(location) {
        if (typeof GameUI !== 'undefined' && GameUI.sendCommand) {
            GameUI.sendCommand(`前往 ${location}`);
        }
        this.closePanel('mapPanel');
    },

    /**
     * 保存游戏 - 修复版本
     */
    async saveGame() {
        try {
            const response = await fetch('/save_game', { method: 'POST' });
            const data = await response.json();

            const msg = document.getElementById('saveLoadMessage');
            if (data.success) {
                msg.textContent = '游戏保存成功！';
                msg.style.color = '#4CAF50';
            } else {
                msg.textContent = '保存失败：' + data.error;
                msg.style.color = '#f44336';
            }
        } catch (error) {
            console.error('保存失败:', error);
            const msg = document.getElementById('saveLoadMessage');
            msg.textContent = '保存失败：网络错误';
            msg.style.color = '#f44336';
        }
    },

    /**
     * 加载游戏 - 修复版本
     */
    async loadGame() {
        try {
            const response = await fetch('/load_game', { method: 'POST' });
            const data = await response.json();

            const msg = document.getElementById('saveLoadMessage');
            if (data.success) {
                msg.textContent = '游戏加载成功！';
                msg.style.color = '#4CAF50';
                // 刷新游戏状态
                if (typeof GameUI !== 'undefined' && GameUI.refreshStatus) {
                    GameUI.refreshStatus();
                }
                setTimeout(() => this.closePanel('saveLoadPanel'), 1000);
            } else {
                msg.textContent = '加载失败：' + data.error;
                msg.style.color = '#f44336';
            }
        } catch (error) {
            console.error('加载失败:', error);
            const msg = document.getElementById('saveLoadMessage');
            msg.textContent = '加载失败：网络错误';
            msg.style.color = '#f44336';
        }
    }
};

// 导出到全局
window.GamePanels = GamePanels;

// 恢复上次打开的面板
window.addEventListener('DOMContentLoaded', () => {
    try {
        const lastPanel = sessionStorage.getItem('sidebar:last');
        if (lastPanel && document.getElementById(lastPanel)) {
            // 延迟一下打开，避免页面未完全加载
            setTimeout(() => {
                console.log(`恢复上次打开的面板: ${lastPanel}`);
                GamePanels.showPanel(lastPanel);
            }, 100);
        }
    } catch (e) {
        console.warn('无法恢复面板状态:', e);
    }
});

console.log('✅ 游戏面板系统已加载 (增强版)');
