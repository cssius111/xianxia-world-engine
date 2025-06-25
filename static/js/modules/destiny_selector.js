const DestinySelector = {
    selected: null,
    onConfirm: null,
    async show(callback) {
        this.onConfirm = callback;
        const modal = document.getElementById('destinySelectModal');
        const container = document.getElementById('destinyOptions');
        if (!modal || !container) return;
        container.innerHTML = '';
        try {
            const res = await fetch('/api/destiny_options');
            const data = await res.json();
            this.options = data.options || [];
            this.options.forEach(opt => {
                const card = document.createElement('div');
                card.className = 'destiny-card';
                card.textContent = opt.name;
                card.dataset.tooltip = opt.description || '';
                card.addEventListener('click', () => {
                    document.querySelectorAll('#destinyOptions .destiny-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    this.selected = opt;
                });
                card.addEventListener('mouseenter', showDestinyTooltip);
                card.addEventListener('mouseleave', hideDestinyTooltip);
                container.appendChild(card);
            });
            modal.style.display = 'flex';
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.transition = 'opacity 0.3s ease';
                modal.style.opacity = '1';
            }, 10);
        } catch (e) {
            console.error('获取命格失败', e);
        }
    },
    hide() {
        const modal = document.getElementById('destinySelectModal');
        if (modal) {
            modal.style.transition = 'opacity 0.3s ease';
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    },
    confirm() {
        if (!this.selected) {
            alert('请选择一个命格');
            return;
        }
        if (typeof this.onConfirm === 'function') {
            this.onConfirm(this.selected);
        }
        this.hide();
    }
};

function showDestinyTooltip(e) {
    const tip = document.getElementById('destinyTooltip');
    if (!tip) return;
    const text = e.currentTarget.dataset.tooltip;
    if (!text) return;
    const rect = e.currentTarget.getBoundingClientRect();
    tip.textContent = text;
    tip.style.left = rect.left + 'px';
    tip.style.top = (rect.top - 30) + 'px';
    tip.classList.add('show');
}

function hideDestinyTooltip() {
    const tip = document.getElementById('destinyTooltip');
    if (tip) tip.classList.remove('show');
}

window.DestinySelector = DestinySelector;
