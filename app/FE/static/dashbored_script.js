document.addEventListener('DOMContentLoaded', function () {
    // Get DOM elements
    const domainInput = document.getElementById('domainInput');
    const addButton = document.querySelector('.add-button');
    const fileUpload = document.getElementById('file-upload');
    const refreshAllButton = document.querySelector('.refresh-button');
    const tableBody = document.getElementById('domainsTableBody');
    const logoutButton = document.querySelector('.header-nav .logout-button');
    const Spinner = document.getElementById('spinner');

    // load the domains data on page load
    getDomainsData()

    // Check schedule status when page loads    
    checkScheduleStatus();

     // Function to toggle spinner visibility
     function spinner(flag) {
        console.log(`Spinner is toggled! with ${flag}`);
        // Spinner.style.display = flag ? 'block' : 'none';
        // same as 
        if (flag) { 
            Spinner.style.display = 'block'; 
        } else { 
            Spinner.style.display = 'none';
        }
    }

    // Logout Button
    logoutButton.addEventListener('click', function () {
        window.location.href = '/logout';
    });

    // Add Domain Button
    addButton.addEventListener('click', function () {
        const domain = domainInput.value.trim();
        if (domain) {
            checkMultipleDomains([domain]);
            domainInput.value = ''; // Clear input after adding
        }
    });

    // Enter key functionality for domain input
    domainInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            const domain = this.value.trim();
            if (domain) {
                checkMultipleDomains([domain]);
                this.value = '';
            }
        }
    });


    fileUpload.addEventListener('change', async function (e) {
        const file = e.target.files[0];
        
        if (file) {
            if (file.name.endsWith(".txt")){
            const reader = new FileReader();
            reader.onload = async function (e) {
                const domains = e.target.result.split('\n')
                    .map(domain => domain.trim())
                    .filter(domain => domain);

                // Basic domain validation regex
                const domainRegex = /^(?:https?:\/\/|https?:\/\/www\.|www\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;

                const validDomains = domains.filter(domain => domainRegex.test(domain));
                const invalidDomains = domains.filter(domain => !domainRegex.test(domain));

                // Create confirmation message
                let confirmMessage = `Found ${domains.length} domains:\n`;
                confirmMessage += `✓ ${validDomains.length} valid domains\n`;
                confirmMessage += `✗ ${invalidDomains.length} invalid domains\n\n`;

                if (invalidDomains.length > 0) {
                    confirmMessage += 'Invalid domains:\n';
                    invalidDomains.forEach(domain => {
                        confirmMessage += `- ${domain}\n`;
                    });
                    confirmMessage += '\n';
                }

                confirmMessage += 'Would you like to proceed with checking the valid domains?';

                // Show confirmation dialog
                if (validDomains.length > 0 && confirm(confirmMessage)) {
                    // Send only valid domains to be checked
                    checkMultipleDomains(validDomains);
                }

                // Reset file input
                fileUpload.value = '';
            };
            reader.readAsText(file);
        }else {
            alert("Please enter a txt file")
        }
    }
    });


    // Refresh All Button
    refreshAllButton.addEventListener('click', function () {
        const rows = tableBody.getElementsByTagName('tr');
        const domains = Array.from(rows).map(row => row.cells[0].textContent);
        checkMultipleDomains(domains);
    });

    // Function to check multiple domains
    async function checkMultipleDomains(domains) {
        spinner(true);
        try {
            const response = await fetch('/check_domains', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ domains: domains })
            });

            if (!response.ok) throw new Error(`Failed to check domains. Status: ${response.status}`);

            const results = await response.json();
            results.forEach(result => addOrUpdateDomainRow(result));
        } catch (error) {
            console.error('Error:', error);
            alert('Error checking multiple domains. Please try again. Details: ' + error.message);
        }
        spinner(false)
    }

    // Function to display domains data from database user
    async function getDomainsData() {
        try {
            const response = await fetch('/get_domains', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },

            });
            if (!response.ok) throw new Error(`Failed to check domains. Status: ${response.status}`);

            const results = await response.json();
            results.forEach(result => addOrUpdateDomainRow(result));
        } catch (error) {
            console.error('Error:', error);
            alert('Error checking multiple domains. Please try again. Details: ' + error.message);
        }
    }



    // Function to add or update domain row
    function addOrUpdateDomainRow(result) {
        const existingRow = Array.from(tableBody.getElementsByTagName('tr'))
            .find(row => row.cells[0].textContent === result.url);

        if (existingRow) {
            updateDomainRow(result);
        } else {
            const tr = document.createElement('tr');
            tr.innerHTML = createRowHTML(result);
            addRowEventListeners(tr);
            tableBody.appendChild(tr);
        }
    }

    // Function to update existing domain row
    function updateDomainRow(result) {
        const rows = tableBody.getElementsByTagName('tr');
        for (let row of rows) {
            if (row.cells[0].textContent === result.url) {
                row.innerHTML = createRowHTML(result);
                addRowEventListeners(row);
                break;
            }
        }
    }

    // Function to create row HTML
    function createRowHTML(result) {
        return `
            <td class = "domain-name">${result.url}</td>
            <td><span class="status-badge ${result.status_code === 'OK' ? 'active' : 'failed'}">${result.status_code}</span></td>
            <td><span class="ssl-badge ${result.ssl_status}">${result.ssl_status}</span></td>
            <td>${result.expiration_date}</td><td>${result.issuer || 'Unknown'}</td>
            <td class="actions-cell">
                <button class="button action-button check-button" data-tooltip="Check Status">
                    <span class="icon">⟳</span>
                </button>
                <button class="button action-button delete-button" data-tooltip="Delete Domain">
                    <span class="icon">×</span>
                </button>
            </td>
        `;
    }

    // Function to add event listeners to row buttons
    function addRowEventListeners(row) {
        const domain = row.cells[0].textContent;

        const checkButton = row.querySelector('.check-button');
        checkButton.addEventListener('click', () => checkMultipleDomains([domain]));

        const deleteButton = row.querySelector('.delete-button');
        deleteButton.addEventListener('click', async function () {
            if (confirm('Are you sure you want to delete this domain?')) {
                try {
                    // Envoie une requête au serveur pour supprimer le domaine
                    const domainElement = row.querySelector('.domain-name');
                    const domain = encodeURIComponent(domainElement.innerHTML.trim());
                    console.log(domain);
                    const response = await fetch(`/remove_domain?domain=${domain}`, {
                        method: 'DELETE', // DELETE sans body
                    });

                    if (response.ok) {
                        // Si la suppression côté serveur réussit, on enlève la ligne de l'interface
                        row.remove();
                        alert('The domain has been successfully deleted.');
                    } else {
                        // Gérer les erreurs renvoyées par le serveur
                        const errorMessage = await response.json();
                        alert(`Failed to delete domain: ${errorMessage}`);
                    }
                } catch (error) {
                    // Gérer les erreurs réseau ou autres
                    console.error('Error:', error);
                    alert('An error occurred while trying to delete the domain.');
                }
            }
        });

    }


    const startScheduleBtn = document.getElementById("startSchedule");
    const stopScheduleBtn = document.getElementById("stopSchedule");
    const hourlyRadio = document.querySelector("input[value='hourly']");
    const dailyRadio = document.querySelector("input[value='daily']");
    const hourlyInterval = document.getElementById("hourlyInterval");
    const dailyTime = document.getElementById("dailyTime");
    const nextRunTime = document.getElementById("nextRunTime");

    async function startSchedule() {
        const domains = Array.from(tableBody.getElementsByTagName('tr'))
            .map(row => row.cells[0].textContent);

        if (domains.length === 0) {
            alert('Please add domains before starting the schedule.');
            return;
        }

        try {
            let response;
            if (hourlyRadio.checked) {
                response = await fetch('/schedule/hourly', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                         interval: parseInt(hourlyInterval.value)
                    })
                });
            } else if (dailyRadio.checked) {
                response = await fetch('/schedule/daily', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        time: dailyTime.value
                    })
                });
            }

            const result = await response.json();
            if (result.status === 'success') {
                startScheduleBtn.disabled = true;
                stopScheduleBtn.disabled = false;
                hourlyInterval.disabled = true;
                dailyTime.disabled = true;
                hourlyRadio.disabled = true;
                dailyRadio.disabled = true;
                nextRunTime.textContent = `Next check: ${new Date(result.next_run).toLocaleString()}`;
            } else {
                alert(`Failed to start schedule: ${result.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to start schedule. Please try again.');
        }
    }


    async function stopSchedule() {
        try {
            const response = await fetch('/schedule/stop', {
                method: 'POST'
            });

            const result = await response.json();
            if (result.status === 'success') {
                startScheduleBtn.disabled = false;
                stopScheduleBtn.disabled = true;
                hourlyInterval.disabled = false;
                dailyTime.disabled = false;
                hourlyRadio.disabled = false;
                dailyRadio.disabled = false;
                nextRunTime.textContent = 'Next check: Not scheduled';
            } else {
                alert(`Failed to stop schedule: ${result.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to stop schedule. Please try again.');
        }
    }


    async function checkScheduleStatus() {
        try {
            const response = await fetch('/schedule/status');
            const result = await response.json();

            if (result.status === 'success' && result.tasks) {
                startScheduleBtn.disabled = true;
                stopScheduleBtn.disabled = false;
                hourlyInterval.disabled = true;
                dailyTime.disabled = true;
                hourlyRadio.disabled = true;
                dailyRadio.disabled = true;
            if (result.tasks[0].next_run){
                let date = new Date(result.tasks[0].next_run).toLocaleString('en-US', {
                    dateStyle: 'short', 
                    timeStyle: 'short'})
                nextRunTime.textContent = `Next check: ${date}`;
            }
            }else{
                startScheduleBtn.disabled = false;
                stopScheduleBtn.disabled = true;
                hourlyInterval.disabled = false;
                dailyTime.disabled = false;
                hourlyRadio.disabled = false;
                dailyRadio.disabled = false;
                nextRunTime.textContent = 'Next check: Not scheduled'
            }
        } catch (error) {
            console.error('Error checking schedule status:', error);
        }
    }

    
    

    startScheduleBtn.addEventListener('click', function () {
        startSchedule()
    });

    stopScheduleBtn.addEventListener('click', function () {
        stopSchedule()
    });
});