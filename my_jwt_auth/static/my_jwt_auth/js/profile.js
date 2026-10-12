(function () {
    if (!requireAuth()) {
        return;
    }

    const els = {
        username: document.getElementById("profile-username"),
        joined: document.getElementById("profile-joined"),
        passwordForm: document.getElementById("change-password-form"),
        passwordMessage: document.getElementById("password-message"),
        passwordSubmit: document.getElementById("change-password-submit"),
        logoutBtn: document.getElementById("logout-btn"),
        deletePrompt: document.getElementById("delete-account-prompt"),
        deleteConfirm: document.getElementById("delete-account-confirm"),
        deleteBtn: document.getElementById("delete-account-btn"),
        deleteCancelBtn: document.getElementById("delete-account-cancel"),
        deleteConfirmBtn: document.getElementById("delete-account-confirm-btn"),
    };

    function formatDate(isoString) {
        const date = new Date(isoString);
        if (Number.isNaN(date.getTime())) return "";
        return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
    }

    function flattenErrors(errorData) {
        if (!errorData || typeof errorData !== "object") {
            return "Не удалось выполнить операцию. Попробуйте ещё раз.";
        }
        const messages = [];
        for (const key of Object.keys(errorData)) {
            const value = errorData[key];
            const items = Array.isArray(value) ? value : [value];
            messages.push(...items);
        }
        return messages.join(" ") || "Не удалось выполнить операцию. Попробуйте ещё раз.";
    }

    function showPasswordMessage(message, isSuccess) {
        els.passwordMessage.textContent = message;
        els.passwordMessage.classList.add("is-visible");
        els.passwordMessage.classList.toggle("is-success", Boolean(isSuccess));
    }

    function hidePasswordMessage() {
        els.passwordMessage.classList.remove("is-visible", "is-success");
    }

    async function loadProfile() {
        try {
            const response = await apiFetch("/api/auth/me/");
            if (!response.ok) {
                showToast("Не удалось загрузить профиль");
                return;
            }
            const user = await response.json();
            els.username.textContent = user.username;
            els.joined.textContent = `На сайте с ${formatDate(user.date_joined)}`;
        } catch (err) {
            showToast("Не удалось загрузить профиль");
        }
    }

    els.passwordForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        hidePasswordMessage();

        const oldPassword = document.getElementById("old-password").value;
        const newPassword = document.getElementById("new-password").value;
        const newPassword2 = document.getElementById("new-password2").value;

        if (newPassword !== newPassword2) {
            showPasswordMessage("Новые пароли не совпадают", false);
            return;
        }

        els.passwordSubmit.disabled = true;
        els.passwordSubmit.textContent = "Сохраняем…";

        try {
            const response = await apiFetch("/api/auth/change-password/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                showPasswordMessage(flattenErrors(errorData), false);
                return;
            }

            els.passwordForm.reset();
            showPasswordMessage("Пароль успешно изменён", true);
        } catch (err) {
            showPasswordMessage("Не удалось подключиться к серверу. Попробуйте ещё раз.", false);
        } finally {
            els.passwordSubmit.disabled = false;
            els.passwordSubmit.textContent = "Сохранить пароль";
        }
    });

    els.logoutBtn.addEventListener("click", () => Auth.logout());

    els.deleteBtn.addEventListener("click", () => {
        els.deletePrompt.hidden = true;
        els.deleteConfirm.hidden = false;
    });

    els.deleteCancelBtn.addEventListener("click", () => {
        els.deleteConfirm.hidden = true;
        els.deletePrompt.hidden = false;
    });

    els.deleteConfirmBtn.addEventListener("click", async () => {
        els.deleteConfirmBtn.disabled = true;
        els.deleteConfirmBtn.textContent = "Удаляем…";

        try {
            const response = await apiFetch("/api/auth/me/", { method: "DELETE" });
            if (!response.ok) {
                showToast("Не удалось удалить аккаунт");
                els.deleteConfirmBtn.disabled = false;
                els.deleteConfirmBtn.textContent = "Да, удалить";
                return;
            }
            Auth.logout();
        } catch (err) {
            showToast("Не удалось удалить аккаунт");
            els.deleteConfirmBtn.disabled = false;
            els.deleteConfirmBtn.textContent = "Да, удалить";
        }
    });

    document.querySelectorAll('[data-nav="home"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            window.location.href = "/";
        });
    });

    document.querySelectorAll('[data-nav="collections"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            window.location.href = "/collections/";
        });
    });

    loadProfile();
})();
