// Password show/hide toggle
document.querySelectorAll(".toggle-password").forEach(function (btn) {
    btn.addEventListener("click", function () {
        var input = document.getElementById(btn.dataset.target);
        if (!input) return;

        var isHidden = input.type === "password";
        input.type = isHidden ? "text" : "password";
        btn.textContent = isHidden ? "Hide" : "Show";
    });
});

// Live password-match + strength check on the signup page
var signupForm = document.getElementById("signup-form");

if (signupForm) {
    var pw1 = document.getElementById("id_password1");
    var pw2 = document.getElementById("id_password2");
    var hint = document.getElementById("signup-hint");

    function checkPasswords() {
        if (!pw1.value || !pw2.value) {
            hint.textContent = "";
            hint.className = "field-hint";
            return;
        }

        if (pw1.value.length < 8) {
            hint.textContent = "Password must be at least 8 characters.";
            hint.className = "field-hint field-hint-error";
        } else if (pw1.value !== pw2.value) {
            hint.textContent = "Passwords do not match.";
            hint.className = "field-hint field-hint-error";
        } else {
            hint.textContent = "Passwords match.";
            hint.className = "field-hint field-hint-ok";
        }
    }

    pw1.addEventListener("input", checkPasswords);
    pw2.addEventListener("input", checkPasswords);

    signupForm.addEventListener("submit", function (e) {
        if (pw1.value.length < 8 || pw1.value !== pw2.value) {
            e.preventDefault();
            checkPasswords();
        }
    });
}