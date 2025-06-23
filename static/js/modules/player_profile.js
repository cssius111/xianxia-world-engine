/**
 * 修仙世界模拟器 - 角色管理器
 * 负责角色信息的管理和展示
 */

class XianxiaPlayerProfile {
    constructor(gameController) {
        this.game = gameController;
        this.playerData = null;
        this.attributeData = null;
        this.cultivationData = null;
        this.achievements = [];
        this.updateInterval = null;
        
        this.init();
    }
    
    /**
     * 初始化角色管理器
     */
    async init() {
        console.log('👤 角色管理器初始化中...');
        
        try {
            // 加载配置数据
            await this.loadConfigData();
            
            // 初始化角色数据
            this.initializePlayerData();
            
            // 设置更新定时器
            this.startUpdateTimer();
            
            console.log('✅ 角色管理器初始化完成');
        } catch (error) {
            console.error('❌ 角色管理器初始化失败:', error);
        }
    }
    
    /**
     * 加载配置数据
     */
    async loadConfigData() {
        try {
            const [attributeRes, cultivationRes, achievementRes] = await Promise.all([
                fetch('/static/data/restructured/attribute_model.json'),
                fetch('/static/data/restructured/cultivation_realm.json'),
                fetch('/static/data/restructured/achievement.json')
            ]);
            
            this.attributeData = await attributeRes.json();
            this.cultivationData = await cultivationRes.json();
            this.achievementData = await achievementRes.json();
            
            console.log('📊 配置数据加载完成');
        } catch (error) {
            console.error('加载配置数据失败:', error);
            throw error;
        }
    }
    
    /**
     * 初始化角色数据
     */
    initializePlayerData() {
        if (this.game.gameState.player) {
            this.playerData = this.game.gameState.player;
            this.updateProfile(this.playerData);
        }
    }
    
    /**
     * 更新角色档案
     */
    updateProfile(playerData) {
        if (!playerData) return;
        
        this.playerData = playerData;
        
        // 更新显示
        this.updateProfileDisplay();
        
        // 检查成就
        this.checkAchievements();
        
        // 计算衍生属性
        this.calculateDerivedAttributes();
        
        // 触发更新事件
        this.triggerProfileUpdate();
    }
    
    /**
     * 更新档案显示
     */
    updateProfileDisplay() {
        if (!this.playerData) return;
        
        // 更新基本信息
        this.updateBasicInfo();
        
        // 更新属性信息
        this.updateAttributeInfo();
        
        // 更新修炼信息
        this.updateCultivationInfo();
        
        // 更新额外信息
        this.updateExtraInfo();
    }
    
    /**
     * 更新基本信息
     */
    updateBasicInfo() {
        const nameElement = document.querySelector('.character-name');
        if (nameElement) {
            nameElement.textContent = this.playerData.name || '无名侠客';
        }
        
        const realmElement = document.querySelector('.character-realm');
        if (realmElement && this.playerData.attributes) {
            const realmInfo = this.getRealmInfo();
            realmElement.textContent = `${realmInfo.name} (${realmInfo.progress}%)`;
        }
    }
    
    /**
     * 更新属性信息
     */
    updateAttributeInfo() {
        if (!this.playerData.attributes) return;
        
        const attributes = this.playerData.attributes;
        
        // 更新数值属性
        this.updateAttributeBar('health', attributes.current_health, attributes.max_health);
        this.updateAttributeBar('mana', attributes.current_mana, attributes.max_mana);
        this.updateAttributeBar('stamina', attributes.current_stamina, attributes.max_stamina);
        this.updateAttributeBar('cultivation', attributes.cultivation_level, attributes.max_cultivation);
        
        // 更新其他属性显示
        this.updateAttributeValues(attributes);
    }
    
    /**
     * 更新属性条
     */
    updateAttributeBar(attributeName, current, max) {
        const bar = document.querySelector(`[data-attribute=\"${attributeName}\"]`);
        if (!bar) return;
        
        const fill = bar.querySelector('.progress-fill');
        const label = bar.querySelector('.attribute-label');
        
        if (fill) {
            const percentage = Math.min(100, Math.max(0, (current / max) * 100));
            fill.style.width = percentage + '%';
            
            // 根据百分比改变颜色
            this.updateProgressBarColor(fill, percentage);
        }
        
        if (label) {
            const valueSpan = label.querySelector('.attribute-value');
            if (valueSpan) {
                valueSpan.textContent = `${current} / ${max}`;
            } else {
                label.innerHTML = `${this.getAttributeDisplayName(attributeName)} <span class=\"attribute-value\">${current} / ${max}</span>`;
            }
        }
    }
    
    /**
     * 更新进度条颜色
     */
    updateProgressBarColor(fill, percentage) {
        if (percentage < 20) {
            fill.style.background = 'linear-gradient(90deg, #ff4444 0%, #ff6666 100%)';
        } else if (percentage < 50) {
            fill.style.background = 'linear-gradient(90deg, #ffaa00 0%, #ffcc44 100%)';
        } else {
            fill.style.background = 'linear-gradient(90deg, var(--brush-gold) 0%, #f4d03f 100%)';
        }
    }
    
    /**
     * 获取属性显示名称
     */
    getAttributeDisplayName(attributeName) {
        const nameMap = {
            'health': '气血',
            'mana': '灵力',
            'stamina': '体力',
            'cultivation': '修为'
        };
        
        return nameMap[attributeName] || attributeName;
    }
    
    /**
     * 更新属性值
     */
    updateAttributeValues(attributes) {
        const attributeElements = document.querySelectorAll('[data-attribute-value]');
        
        attributeElements.forEach(element => {
            const attrName = element.dataset.attributeValue;
            const value = attributes[attrName];
            
            if (value !== undefined) {
                element.textContent = value;
            }
        });
    }
    
    /**
     * 更新修炼信息
     */
    updateCultivationInfo() {
        if (!this.playerData.attributes) return;
        
        const realmInfo = this.getRealmInfo();
        const cultivationElement = document.querySelector('.cultivation-info');
        
        if (cultivationElement) {
            cultivationElement.innerHTML = `
                <div class=\"realm-name\">${realmInfo.name}</div>
                <div class=\"realm-level\">${realmInfo.subLevel}</div>
                <div class=\"realm-progress\">${realmInfo.progress}%</div>
            `;
        }
    }
    
    /**
     * 获取境界信息
     */
    getRealmInfo() {
        const attributes = this.playerData.attributes;
        const realmName = attributes.realm_name || '炼气期';
        const realmLevel = attributes.realm_level || 1;
        const realmProgress = attributes.realm_progress || 0;
        
        // 从配置数据获取详细信息
        const realmData = this.cultivationData?.realms?.[realmName];
        
        let subLevel = '';
        if (realmData && realmData.sub_levels) {
            const subLevelIndex = Math.min(realmLevel - 1, realmData.sub_levels.length - 1);
            if (subLevelIndex >= 0) {
                subLevel = realmData.sub_levels[subLevelIndex].name;
            }
        }
        
        return {
            name: realmName,
            level: realmLevel,
            subLevel: subLevel,
            progress: Math.round(realmProgress)
        };
    }
    
    /**
     * 更新额外信息
     */
    updateExtraInfo() {
        if (!this.playerData.extra_data) return;
        
        const extraData = this.playerData.extra_data;
        
        // 更新门派信息
        if (extraData.faction) {
            this.updateFactionInfo(extraData.faction);
        }
        
        // 更新灵根信息
        if (extraData.spiritual_root) {
            this.updateSpiritualRootInfo(extraData.spiritual_root);
        }
        
        // 更新其他信息
        this.updateOtherInfo(extraData);
    }
    
    /**
     * 更新门派信息
     */
    updateFactionInfo(faction) {
        const factionElement = document.querySelector('.faction-info');
        if (factionElement) {
            factionElement.textContent = faction;
        }
        
        // 更新角色名称显示中的门派
        const nameElement = document.querySelector('.character-name');
        if (nameElement) {
            const baseName = this.playerData.name || '无名侠客';
            nameElement.textContent = `${baseName}(${faction})`;
        }
    }
    
    /**
     * 更新灵根信息
     */
    updateSpiritualRootInfo(spiritualRoot) {
        const rootElement = document.querySelector('.spiritual-root-info');
        if (rootElement) {
            rootElement.textContent = spiritualRoot;
        }
    }
    
    /**
     * 更新其他信息
     */
    updateOtherInfo(extraData) {
        // 更新年龄
        if (extraData.age) {
            const ageElement = document.querySelector('.character-age');
            if (ageElement) {
                ageElement.textContent = `${extraData.age}岁`;
            }
        }
        
        // 更新性别
        if (extraData.gender) {
            const genderElement = document.querySelector('.character-gender');
            if (genderElement) {
                genderElement.textContent = extraData.gender;
            }
        }
        
        // 更新其他自定义属性
        Object.keys(extraData).forEach(key => {
            const element = document.querySelector(`[data-extra-${key}]`);
            if (element) {
                element.textContent = extraData[key];
            }
        });
    }
    
    /**
     * 计算衍生属性
     */
    calculateDerivedAttributes() {
        if (!this.playerData.attributes || !this.attributeData) return;
        
        const attributes = this.playerData.attributes;
        const derivedFormulas = this.attributeData.derived_attributes;
        
        // 计算修炼速度
        if (derivedFormulas.cultivation_speed) {
            const comprehension = attributes.comprehension || 5;
            const baseSpeed = 1.0;
            attributes.cultivation_speed = baseSpeed * (1 + comprehension * 0.1);
        }
        
        // 计算暴击率
        if (derivedFormulas.critical_rate) {
            const luck = attributes.luck || 5;
            attributes.critical_rate = 5 + luck * 2;
        }
        
        // 计算闪避率
        if (derivedFormulas.dodge_rate) {
            const speed = attributes.speed || 10;
            attributes.dodge_rate = speed * 0.5;
        }
        
        // 更新显示
        this.updateDerivedAttributeDisplay();
    }
    
    /**
     * 更新衍生属性显示
     */
    updateDerivedAttributeDisplay() {
        const attributes = this.playerData.attributes;
        
        // 更新修炼速度
        const cultivationSpeedElement = document.querySelector('.cultivation-speed');
        if (cultivationSpeedElement && attributes.cultivation_speed) {
            cultivationSpeedElement.textContent = `${attributes.cultivation_speed.toFixed(2)}x`;
        }
        
        // 更新暴击率
        const criticalRateElement = document.querySelector('.critical-rate');
        if (criticalRateElement && attributes.critical_rate) {
            criticalRateElement.textContent = `${attributes.critical_rate.toFixed(1)}%`;
        }
        
        // 更新闪避率
        const dodgeRateElement = document.querySelector('.dodge-rate');
        if (dodgeRateElement && attributes.dodge_rate) {
            dodgeRateElement.textContent = `${attributes.dodge_rate.toFixed(1)}%`;
        }
    }
    
    /**
     * 检查成就
     */
    checkAchievements() {
        if (!this.achievementData || !this.playerData) return;
        
        const achievements = this.achievementData.achievements;
        const newAchievements = [];
        
        // 检查各类成就
        Object.keys(achievements).forEach(category => {
            const categoryAchievements = achievements[category];
            
            Object.keys(categoryAchievements).forEach(achievementId => {
                const achievement = categoryAchievements[achievementId];
                
                if (this.checkAchievementRequirements(achievement)) {
                    if (!this.achievements.includes(achievement.id)) {
                        newAchievements.push(achievement);
                        this.achievements.push(achievement.id);
                    }
                }
            });
        });
        
        // 显示新成就
        if (newAchievements.length > 0) {
            this.showNewAchievements(newAchievements);
        }
    }
    
    /**
     * 检查成就要求
     */
    checkAchievementRequirements(achievement) {
        if (!achievement.requirements) return false;
        
        const requirements = achievement.requirements;
        const attributes = this.playerData.attributes;
        const extraData = this.playerData.extra_data || {};
        
        // 检查境界要求
        if (requirements.realm) {
            const currentRealm = attributes.realm_name || '炼气期';
            if (currentRealm !== requirements.realm) return false;
        }
        
        // 检查等级要求
        if (requirements.level) {
            const currentLevel = attributes.level || 1;
            if (currentLevel < requirements.level) return false;
        }
        
        // 检查修炼次数
        if (requirements.cultivation_count) {
            const cultivationCount = extraData.cultivation_count || 0;
            if (cultivationCount < requirements.cultivation_count) return false;
        }
        
        // 检查特殊条件
        if (requirements.legendary_spiritual_root) {
            const spiritualRoot = extraData.spiritual_root || '';
            if (!this.isLegendaryRoot(spiritualRoot)) return false;
        }
        
        return true;
    }
    
    /**
     * 检查是否为传说灵根
     */
    isLegendaryRoot(spiritualRoot) {
        const legendaryRoots = ['雷灵根', '冰灵根', '风灵根', '光灵根', '暗灵根'];
        return legendaryRoots.includes(spiritualRoot);
    }
    
    /**
     * 显示新成就
     */
    showNewAchievements(achievements) {
        achievements.forEach(achievement => {
            this.showAchievementNotification(achievement);
            
            // 播放成就音效
            if (this.game.modules.audio) {
                this.game.modules.audio.playSuccessSound();
            }
        });
    }
    
    /**
     * 显示成就通知
     */
    showAchievementNotification(achievement) {
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class=\"achievement-icon\">${this.getAchievementIcon(achievement.category)}</div>
            <div class=\"achievement-content\">
                <div class=\"achievement-title\">🏆 成就达成</div>
                <div class=\"achievement-name\">${achievement.name}</div>
                <div class=\"achievement-description\">${achievement.description}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // 动画效果
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // 自动移除
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
    
    /**
     * 获取成就图标
     */
    getAchievementIcon(category) {
        const iconMap = {
            '修炼成就': '🧘',
            '战斗成就': '⚔️',
            '探索成就': '🗺️',
            '社交成就': '🤝',
            '收集成就': '📦',
            '技能成就': '📚',
            '特殊成就': '⭐'
        };
        
        return iconMap[category] || '🏆';
    }
    
    /**
     * 获取角色统计信息
     */
    getPlayerStats() {
        if (!this.playerData) return null;
        
        const attributes = this.playerData.attributes;
        const extraData = this.playerData.extra_data || {};
        
        return {
            basic: {
                name: this.playerData.name,
                level: attributes.level,
                realm: attributes.realm_name,
                faction: extraData.faction,
                spiritual_root: extraData.spiritual_root
            },
            attributes: {
                health: `${attributes.current_health}/${attributes.max_health}`,
                mana: `${attributes.current_mana}/${attributes.max_mana}`,
                stamina: `${attributes.current_stamina}/${attributes.max_stamina}`,
                cultivation: `${attributes.cultivation_level}/${attributes.max_cultivation}`,
                attack: attributes.attack_power,
                defense: attributes.defense,
                speed: attributes.speed
            },
            derived: {
                cultivation_speed: attributes.cultivation_speed,
                critical_rate: attributes.critical_rate,
                dodge_rate: attributes.dodge_rate
            },
            achievements: this.achievements.length,
            extra: extraData
        };
    }
    
    /**
     * 导出角色数据
     */
    exportPlayerData() {
        const stats = this.getPlayerStats();
        
        const exportData = {
            player: this.playerData,
            stats: stats,
            achievements: this.achievements,
            timestamp: Date.now()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `character_${this.playerData.name}_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        console.log('角色数据已导出');
    }
    
    /**
     * 启动更新定时器
     */
    startUpdateTimer() {
        this.updateInterval = setInterval(() => {
            if (this.game.gameState.player) {
                this.updateProfile(this.game.gameState.player);
            }
        }, 5000); // 每5秒更新一次
    }
    
    /**
     * 停止更新定时器
     */
    stopUpdateTimer() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    /**
     * 触发档案更新事件
     */
    triggerProfileUpdate() {
        const event = new CustomEvent('profileUpdate', {
            detail: {
                player: this.playerData,
                stats: this.getPlayerStats()
            }
        });
        
        document.dispatchEvent(event);
    }
    
    /**
     * 渲染
     */
    render() {
        // 实时更新某些数值
        this.updateRealTimeValues();
    }
    
    /**
     * 更新实时数值
     */
    updateRealTimeValues() {
        // 这里可以添加需要实时更新的数值
        // 例如：生命值恢复、灵力恢复等
    }
    
    /**
     * 销毁角色管理器
     */
    destroy() {
        this.stopUpdateTimer();
        
        // 清理数据
        this.playerData = null;
        this.attributeData = null;
        this.cultivationData = null;
        this.achievements = [];
        
        console.log('👤 角色管理器已销毁');
    }
}

// 导出供其他模块使用
window.XianxiaPlayerProfile = XianxiaPlayerProfile;