const loginButton = document.getElementById('login');
const registerButton = document.getElementById('register');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');


registerButton.addEventListener('click', function() {
    window.location.assign('/register');
});



/*loginButton.addEventListener('click', async function() {
    let username = usernameInput.value;
    let password = passwordInput.value;
    const login_status = await fetch(`/login?username=${username}&password=${password}`);*/

       


