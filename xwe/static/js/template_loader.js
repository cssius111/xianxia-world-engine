const TemplateLoader = (() => {
    async function loadTemplates() {
        const res = await fetch('/data/templates');
        if (!res.ok) {
            throw new Error('加载模板失败');
        }
        return await res.json();
    }
    return { loadTemplates };
})();

window.templateLoader = TemplateLoader;
