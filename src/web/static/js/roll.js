/**
 * 抽卡页面逻辑
 */

// 获取URL参数
const urlParams = new URLSearchParams(window.location.search);
const rollMode = urlParams.get('mode') || 'random';

// DOM元素
const rollBtn = document.getElementById('roll-btn');
const rollArea = document.getElementById('roll-area');
const jackpotModal = document.getElementById('jackpot-modal');
const modalClose = document.querySelector('.modal-close');
const confirmBtn = document.getElementById('confirmButton');

// 当前角色数据
let currentCharacter = null;

// 属性中文名映射
const attrNames = {
    comprehension: '悟性',
    constitution: '根骨',
    fortune: '气运',
    charisma: '魅力',
    willpower: '毅力',
    perception: '感知',
    destiny: '天命',
    opportunity: '机缘'
};

// 属性值到品阶的映射
function getAttrClass(value) {
    if (value >= 10) return 'attr-value-10';
    if (value >= 8) return `attr-value-${value}`;
    if (value >= 6) return `attr-value-${value}`;
    if (value >= 4) return `attr-value-${value}`;
    return `attr-value-${value}`;
}

// 显示角色属性
function displayCharacter(character) {
    // 基础信息
    document.getElementById('char-name').textContent = character.name || '未知';
    document.getElementById('char-age').textContent = character.age || '20';
    document.getElementById('char-spiritual-root').textContent = character.spiritual_root || '无';
    
    // 八维属性
    for (const [key, value] of Object.entries(character.attributes)) {
        const elem = document.getElementById(`attr-${key}`);
        if (elem) {
            elem.textContent = value;
            elem.className = `attribute-value ${getAttrClass(value)}`;
            
            // 添加滚动动画
            elem.classList.add('rolling');
            setTimeout(() => elem.classList.remove('rolling'), 300);
        }
    }
}

// 检查并显示jackpot
function checkAndShowJackpot(character) {
    const highAttrs = Object.values(character.attributes).filter(v => v >= 8).length;
    
    if (highAttrs >= 2) {
        showJackpot('大保底', `你的角色有${highAttrs}项属性达到8以上，天纵奇才！`);
    } else if (highAttrs >= 1) {
        showJackpot('小保底', '你的角色拥有超凡天赋！');
    }
}

// 显示jackpot模态框
function showJackpot(type, description) {
    document.getElementById('jackpot-title').textContent = `✨ 触发${type}！`;
    document.getElementById('jackpot-desc').textContent = description;
    jackpotModal.style.display = 'block';
    
    // 添加发光效果
    document.getElementById('jackpot-title').classList.add('jackpot-glow');
}

// 执行抽卡
async function performRoll() {
    rollBtn.disabled = true;
    rollBtn.textContent = '抽取中...';
    
    // 显示抽取动画
    rollArea.innerHTML = '<p class="text-2xl">命运轮盘转动中...</p>';
    
    try {
        const response = await fetch('/api/roll', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mode: rollMode,
                type: rollMode === 'template' ? getTemplateType() : null,
                prompt: rollMode === 'custom' ? getCustomPrompt() : null
            })
        });
        
        if (!response.ok) {
            throw new Error('抽卡失败');
        }
        
        const data = await response.json();
        currentCharacter = data.character;

        // 显示结果
        displayCharacter(currentCharacter);
        rollArea.innerHTML = '<p class="text-2xl text-accent">天命已定！</p>';

        // 检查jackpot
        checkAndShowJackpot(currentCharacter);

        // 显示确认按钮以等待玩家决定是否创建角色
        if (confirmBtn) {
            confirmBtn.style.display = 'inline-block';
        }

        rollBtn.textContent = '重新抽取';
        
    } catch (error) {
        console.error('Roll error:', error);
        rollArea.innerHTML = '<p class="text-xl text-accent">抽取失败，请重试</p>';
        rollBtn.textContent = '重新抽取';
    } finally {
        rollBtn.disabled = false;
    }
}

// 获取模板类型（如果是模板模式）
function getTemplateType() {
    // TODO: 实现模板选择UI
    return 'sword'; // 暂时默认剑修
}

// 获取自定义提示词（如果是自定义模式）
function getCustomPrompt() {
    // TODO: 实现自定义输入UI
    return '一个天赋异禀的少年剑客';
}

// 确认创建角色
async function confirmCharacter() {
    if (!currentCharacter) {
        alert('请先抽取角色');
        return;
    }

    confirmBtn.disabled = true;
    confirmBtn.textContent = '创建中...';

    const payload = {
        name: currentCharacter.name,
        gender: 'male',
        background: 'auto',
        attributes: currentCharacter.attributes,
    };
    const devParam = localStorage.getItem('dev') === 'true' ? '?dev=true' : '';

    try {
        const res = await fetch(`/create_character${devParam}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const result = await res.json();
        if (result.success) {
            window.location.href = '/game' + (devParam ? '&mode=dev' : '');
        } else {
            alert('创建角色失败：' + (result.error || '未知错误'));
        }
    } catch (err) {
        alert('创建角色失败：' + err.message);
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = '确认创建';
    }
}


// 事件监听
rollBtn.addEventListener('click', performRoll);
if (confirmBtn) {
    confirmBtn.addEventListener('click', confirmCharacter);
}

// 模态框关闭
modalClose.addEventListener('click', () => {
    jackpotModal.style.display = 'none';
});

window.addEventListener('click', (event) => {
    if (event.target === jackpotModal) {
        jackpotModal.style.display = 'none';
    }
});

// 页面加载完成后
document.addEventListener('DOMContentLoaded', () => {
    // 如果是模板或自定义模式，可能需要先显示选择界面
    if (rollMode === 'template') {
        // TODO: 显示模板选择
    } else if (rollMode === 'custom') {
        // TODO: 显示输入框
    }
});
