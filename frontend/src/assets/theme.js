/* 全局深浅色主题切换 */
(function () {
    const KEY = 'art-theme';

    function current() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    function updateButtons() {
        const dark = current() === 'dark';
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.textContent = dark ? '☀️' : '🌙';
            btn.title = dark ? '切换到浅色模式' : '切换到深色模式';
        });
    }

    function apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try {
            localStorage.setItem(KEY, theme);
        } catch (e) { /* 忽略隐私模式等场景 */ }
        updateButtons();
    }

    // 切换：供页面按钮调用
    window.toggleTheme = function () {
        apply(current() === 'dark' ? 'light' : 'dark');
    };

    // 初始化：优先本地存储，其次系统偏好；在 head 中同步执行以避免闪屏
    let theme = null;
    try {
        theme = localStorage.getItem(KEY);
    } catch (e) { /* 忽略 */ }
    if (!theme) {
        theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', theme);
    document.addEventListener('DOMContentLoaded', updateButtons);
})();
