const usernameInput = document.getElementById('username');
const userAvalaibility = document.getElementById('avaliabilityStatus');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirm-password');
const errorDiv = document.getElementById('error');
const form = document.querySelector('form');
let isUsernameAvailable = false;
let timeout = null;


usernameInput.addEventListener('input',async function(){
    const user = usernameInput.value;
    
    if (user.length < 5) {
        userAvalaibility.innerHTML = `<span style="color: grey;">Type at least 5 characters</span>`;
        isUsernameAvailable = false;
        clearTimeout(timeout); 
        return;
    }

    clearTimeout(timeout); // Annule le délai précédent
    timeout = setTimeout(async () => {
        try {
            const response = await fetch(`/checkUserAvaliability?username=${encodeURIComponent(user)}`);
            console.log('API Response Status:', response.status);
            const isAvailable = await response.json();
        
                if (isAvailable.available){
                    userAvalaibility.innerHTML = `<span style="color: green;">User is available</span>`;
                    isUsernameAvailable = true;
                }else{
                    userAvalaibility.innerHTML = `<span style="color : red">User in use</span>`
                    isUsernameAvailable = false;
                } ;
            } catch (error) {
                console.error('Error:', error);
                alert('Error checking users. Please try again.');
                isUsernameAvailable = false;
            }
        }, 300);
});

passwordInput.addEventListener('input', function(){
    errorDiv.innerHTML = "";
});

confirmPasswordInput.addEventListener('input', function(){
    errorDiv.innerHTML = "";
});

form.addEventListener('submit', function (event) {
    if (!isUsernameAvailable) {
        event.preventDefault(); // Bloque l'envoi du formulaire
        
    }

    if (passwordInput.value !== confirmPasswordInput.value) {        
        event.preventDefault(); // Bloque l'envoi du formulaire
        errorDiv.innerHTML = "Passwords do not match";
        errorDiv.style.color = "red";
    }
});