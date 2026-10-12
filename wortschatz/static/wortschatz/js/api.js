/* Shared auth + fetch helpers used across pages. */

const Auth = {
    getAccess() {
        return localStorage.getItem("access");
    },
    getRefresh() {
        return localStorage.getItem("refresh");
    },
    setTokens(access, refresh) {
        localStorage.setItem("access", access);
        if (refresh) {
            localStorage.setItem("refresh", refresh);
        }
    },
    clear() {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
    },
    isLoggedIn() {
        return Boolean(this.getAccess());
    },
    logout(redirectTo = "/login/") {
        this.clear();
        window.location.href = redirectTo;
    },
    async refreshAccessToken() {
        const refresh = this.getRefresh();
        if (!refresh) {
            return false;
        }
        try {
            const response = await fetch("/api/auth/token/refresh/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ refresh }),
            });
            if (!response.ok) {
                return false;
            }
            const data = await response.json();
            this.setTokens(data.access, null);
            return true;
        } catch (err) {
            return false;
        }
    },
};

/**
 * Fetch wrapper that attaches the JWT access token and transparently
 * retries once after a silent token refresh on a 401.
 */
async function apiFetch(url, options = {}) {
    const headers = new Headers(options.headers || {});
    const access = Auth.getAccess();
    if (access) {
        headers.set("Authorization", `Bearer ${access}`);
    }

    let response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        const refreshed = await Auth.refreshAccessToken();
        if (refreshed) {
            headers.set("Authorization", `Bearer ${Auth.getAccess()}`);
            response = await fetch(url, { ...options, headers });
        }
    }

    if (response.status === 401) {
        Auth.logout();
        return response;
    }

    return response;
}

/** Redirects to /login/ if there is no access token. Call at the top of protected pages. */
function requireAuth() {
    if (!Auth.isLoggedIn()) {
        window.location.href = "/login/";
        return false;
    }
    return true;
}

function showToast(message, duration = 2200) {
    let root = document.getElementById("toast-root");
    if (!root) {
        root = document.createElement("div");
        root.id = "toast-root";
        document.body.appendChild(root);
    }

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    root.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("is-visible"));

    setTimeout(() => {
        toast.classList.remove("is-visible");
        setTimeout(() => toast.remove(), 250);
    }, duration);
}

/**
 * Russian plural selection. forms = [one, few, many], e.g. ["слово", "слова", "слов"].
 */
function pluralizeRu(n, forms) {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return forms[0];
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return forms[1];
    return forms[2];
}
