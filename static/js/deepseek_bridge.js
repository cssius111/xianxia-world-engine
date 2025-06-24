const DeepSeekBridge = (() => {
    async function parseCustomText(text) {
        const res = await fetch('/api/parse_custom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        if (!res.ok) {
            throw new Error('解析失败');
        }
        const data = await res.json();
        if (!data.success) {
            throw new Error(data.error || '解析失败');
        }
        return data.data;
    }
    return { parseCustomText };
})();

window.deepSeekBridge = DeepSeekBridge;
