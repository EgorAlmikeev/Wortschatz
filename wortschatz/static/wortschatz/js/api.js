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

function showToast(message, duration = 2200, variant = "default") {
    let root = document.getElementById("toast-root");
    if (!root) {
        root = document.createElement("div");
        root.id = "toast-root";
        document.body.appendChild(root);
    }

    const toast = document.createElement("div");
    toast.className = variant === "warning" ? "toast toast-warning" : "toast";
    toast.textContent = message;
    root.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("is-visible"));

    setTimeout(() => {
        toast.classList.remove("is-visible");
        setTimeout(() => toast.remove(), 250);
    }, duration);
}

/**
 * Small centered Yes/No dialog, layered above any open modal. Resolves to
 * true if the user confirmed, false if they cancelled or clicked outside.
 */
function confirmDialog(options) {
    options = options || {};
    return new Promise((resolve) => {
        const overlay = document.createElement("div");
        overlay.className = "confirm-overlay";
        overlay.innerHTML = `
            <div class="confirm-dialog" role="alertdialog" aria-modal="true">
                <p class="confirm-message"></p>
                <div class="confirm-actions">
                    <button type="button" class="btn btn-surface confirm-cancel"></button>
                    <button type="button" class="btn confirm-ok"></button>
                </div>
            </div>
        `;
        overlay.querySelector(".confirm-message").textContent = options.message || "";
        overlay.querySelector(".confirm-cancel").textContent = options.cancelText || "Отмена";
        const okBtn = overlay.querySelector(".confirm-ok");
        okBtn.textContent = options.confirmText || "Да";
        okBtn.classList.add(options.danger ? "btn-danger" : "btn-mint");

        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add("is-open"));

        function finish(result) {
            overlay.classList.remove("is-open");
            setTimeout(() => overlay.remove(), 200);
            resolve(result);
        }

        overlay.querySelector(".confirm-cancel").addEventListener("click", () => finish(false));
        okBtn.addEventListener("click", () => finish(true));
        overlay.addEventListener("click", (event) => {
            if (event.target === overlay) finish(false);
        });
    });
}

/**
 * Small centered dialog with a single labeled text input, layered above any
 * open modal. Resolves to the trimmed input value on submit, or null if
 * cancelled (overlay click or Escape). The submit button stays disabled
 * while the input is empty.
 */
function promptDialog(options) {
    options = options || {};
    return new Promise((resolve) => {
        const overlay = document.createElement("div");
        overlay.className = "confirm-overlay";
        overlay.innerHTML = `
            <div class="confirm-dialog" role="dialog" aria-modal="true">
                <h3 class="prompt-title"></h3>
                <div class="field">
                    <label class="prompt-label"></label>
                    <input class="input prompt-input" type="text" autocomplete="off">
                </div>
                <button type="button" class="btn btn-mint btn-block prompt-submit" disabled></button>
            </div>
        `;
        overlay.querySelector(".prompt-title").textContent = options.title || "";
        overlay.querySelector(".prompt-label").textContent = options.label || "";
        const input = overlay.querySelector(".prompt-input");
        input.placeholder = options.placeholder || "";
        if (options.maxLength) {
            input.maxLength = options.maxLength;
        }
        const submitBtn = overlay.querySelector(".prompt-submit");
        submitBtn.textContent = options.submitText || "Создать";

        document.body.appendChild(overlay);
        requestAnimationFrame(() => {
            overlay.classList.add("is-open");
            input.focus();
        });

        function finish(result) {
            overlay.classList.remove("is-open");
            setTimeout(() => overlay.remove(), 200);
            resolve(result);
        }

        input.addEventListener("input", () => {
            submitBtn.disabled = input.value.trim().length === 0;
        });
        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && !submitBtn.disabled) {
                finish(input.value.trim());
            } else if (event.key === "Escape") {
                finish(null);
            }
        });
        submitBtn.addEventListener("click", () => {
            if (!submitBtn.disabled) {
                finish(input.value.trim());
            }
        });
        overlay.addEventListener("click", (event) => {
            if (event.target === overlay) finish(null);
        });
    });
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
