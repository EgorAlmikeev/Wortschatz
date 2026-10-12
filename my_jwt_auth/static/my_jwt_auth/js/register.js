(function () {
    if (Auth.isLoggedIn()) {
        window.location.href = "/";
        return;
    }

    const form = document.getElementById("register-form");
    const errorBox = document.getElementById("auth-error");
    const submitBtn = document.getElementById("register-submit");

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.add("is-visible");
    }

    function hideError() {
        errorBox.classList.remove("is-visible");
    }

    function flattenErrors(errorData) {
        if (!errorData || typeof errorData !== "object") {
            return "Не удалось зарегистрироваться. Попробуйте ещё раз.";
        }
        const messages = [];
        for (const key of Object.keys(errorData)) {
            const value = errorData[key];
            const items = Array.isArray(value) ? value : [value];
            messages.push(...items);
        }
        return messages.join(" ") || "Не удалось зарегистрироваться. Попробуйте ещё раз.";
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        hideError();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;
        const password2 = document.getElementById("password2").value;

        if (password !== password2) {
            showError("Пароли не совпадают");
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = "Создаём аккаунт…";

        try {
            const response = await fetch("/api/auth/register/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                showError(flattenErrors(errorData));
                return;
            }

            // Registered — log in right away so the user lands on a populated word list.
            const tokenResponse = await fetch("/api/auth/token/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (tokenResponse.ok) {
                const data = await tokenResponse.json();
                Auth.setTokens(data.access, data.refresh);
                window.location.href = "/";
            } else {
                window.location.href = "/login/";
            }
        } catch (err) {
            showError("Не удалось подключиться к серверу. Попробуйте ещё раз.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Зарегистрироваться";
        }
    });
})();
