(function () {
    // Already logged in? Skip the form entirely.
    if (Auth.isLoggedIn()) {
        window.location.href = "/";
        return;
    }

    const form = document.getElementById("login-form");
    const errorBox = document.getElementById("auth-error");
    const submitBtn = document.getElementById("login-submit");

    function showError(message) {
        errorBox.textContent = message;
        errorBox.classList.add("is-visible");
    }

    function hideError() {
        errorBox.classList.remove("is-visible");
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        hideError();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;

        submitBtn.disabled = true;
        submitBtn.textContent = "Входим…";

        try {
            const response = await fetch("/api/auth/token/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                showError("Неверный логин или пароль");
                return;
            }

            const data = await response.json();
            Auth.setTokens(data.access, data.refresh);
            window.location.href = "/";
        } catch (err) {
            showError("Не удалось подключиться к серверу. Попробуйте ещё раз.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Войти";
        }
    });
})();
