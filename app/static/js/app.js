/**
 * AI News Hub - Client Interactivity
 */

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initRefreshButtons();
});

/* ==================== THEME MANAGEMENT ==================== */
function initTheme() {
    const themeToggleBtn = document.getElementById("themeToggle");
    const htmlEl = document.documentElement;

    // Retrieve stored or system preference
    const storedTheme = localStorage.getItem("ai_news_hub_theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = storedTheme || (prefersDark ? "dark" : "light");

    setTheme(initialTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = htmlEl.getAttribute("data-theme") || "light";
            const nextTheme = currentTheme === "dark" ? "light" : "dark";
            setTheme(nextTheme);
        });
    }

    function setTheme(theme) {
        htmlEl.setAttribute("data-theme", theme);
        localStorage.setItem("ai_news_hub_theme", theme);
    }
}

/* ==================== MANUAL RSS REFRESH ==================== */
function initRefreshButtons() {
    const quickRefreshBtn = document.getElementById("quickRefreshBtn");
    const adminRefreshBtn = document.getElementById("adminRefreshBtn");

    const handleRefresh = async (btn) => {
        if (!btn) return;
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<span class="refresh-spinner">⏳</span> Fetching Feeds...`;

        try {
            const res = await fetch("/api/admin/refresh", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            if (res.status === 409) {
                showToast("A news collection job is already running in background.", "warning");
            } else if (res.ok) {
                const data = await res.json();
                showToast("News feeds refreshed successfully! Reloading...", "success");
                setTimeout(() => window.location.reload(), 1500);
            } else {
                showToast("Error triggering feed collection.", "danger");
            }
        } catch (err) {
            console.error("Refresh error:", err);
            showToast("Network error contacting server.", "danger");
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    };

    if (quickRefreshBtn) {
        quickRefreshBtn.addEventListener("click", () => handleRefresh(quickRefreshBtn));
    }
    if (adminRefreshBtn) {
        adminRefreshBtn.addEventListener("click", () => handleRefresh(adminRefreshBtn));
    }
}

/* ==================== TOAST NOTIFICATIONS ==================== */
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "warning") icon = "⚠️";
    if (type === "danger") icon = "❌";

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
