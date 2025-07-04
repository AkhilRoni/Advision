// Sidebar script
const sidebar = document.querySelector(".sidebar");
const sidebarToggler = document.querySelector(".sidebar-toggler");
const menuToggler = document.querySelector(".menu-toggler");
let collapsedSidebarHeight = "56px";
let fullSidebarHeight = "calc(100vh - 32px)";

document.addEventListener("DOMContentLoaded", () => {
   // sidebar.classList.add("collapsed");
});

// Toggle sidebar's collapsed state
sidebarToggler.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    updateDropdownVisibility(); // Update dropdown visibility when sidebar state changes
});
// Update sidebar height and menu toggle text
const toggleMenu = (isMenuActive) => {
    sidebar.style.height = isMenuActive ? `${sidebar.scrollHeight}px` : collapsedSidebarHeight;
    menuToggler.querySelector("span").innerText = isMenuActive ? "close" : "menu";
};
// Toggle menu-active class and adjust height
menuToggler.addEventListener("click", () => {
    toggleMenu(sidebar.classList.toggle("menu-active"));
});
// Dropdown functionality
document.addEventListener("DOMContentLoaded", function () {
    const dropdownToggle = document.querySelector(".nav-item.dropdown .nav-link");
    const dropdown = document.querySelector(".nav-item.dropdown");
    const dropdownList = dropdown.querySelector(".dropdown-list");

    dropdownToggle.addEventListener("click", function (e) {
        e.preventDefault();
        // Toggle the dropdown active state
        dropdown.classList.toggle("active");
        // Update dropdown visibility based on sidebar state
        updateDropdownVisibility();
        // If sidebar is collapsed, ensure dropdown is visible
        if (sidebar.classList.contains("collapsed")) {
            const dropdownList = dropdown.querySelector(".dropdown-list");
            if (dropdown.classList.contains("active")) {
                dropdownList.style.display = "block";
            } else {
                dropdownList.style.display = "none";
            }
        }
    });
    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove("active");
            updateDropdownVisibility();
        }
    });
    // Function to update dropdown visibility based on sidebar state
    function updateDropdownVisibility() {
        if (sidebar.classList.contains("collapsed")) {
            if (dropdown.classList.contains("active")) {
                dropdownList.style.display = "block";
            } else {
                dropdownList.style.display = "none";
            }
        } else {
            // If sidebar is not collapsed, ensure dropdown list is visible (if active)
            dropdownList.style.display = dropdown.classList.contains("active") ? "block" : "none";
        }
    }
});

document.addEventListener("DOMContentLoaded", () => {
    fetchTimeDistribution(); // Fetch data when the page loads
});

async function fetchTimeDistribution() {
    try {
        const response = await fetch("http://127.0.0.1:8000/analytics/time-distribution");
        const data = await response.json();
        updateTimeDistChart(data.time_distribution);
    } catch (error) {
        console.error("Error fetching time distribution data:", error);
    }
}

function updateTimeDistChart(data) {
    const timeLabels = [
        '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', 
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 
        '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', 
        '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM'
    ];
    
    // Map backend data to chart format
    let timeValues = timeLabels.map((_, index) => data[index] || 0);

    // Update chart
    timedistChart.data.labels = timeLabels;
    timedistChart.data.datasets[0].data = timeValues;
    timedistChart.update();
}

// Initialize Chart
const ctxTimeDist = document.getElementById('timedistChart').getContext('2d');
const timedistChart = new Chart(ctxTimeDist, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Interactions',
            data: [],
            backgroundColor: 'rgba(33, 150, 243, 0.2)',
            borderColor: '#2196F3',
            borderWidth: 2,
            pointBackgroundColor: '#2196F3',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#FF5722',
            pointHoverBorderColor: '#FF5722',
            tension: 0.4 // Smooth curve
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: { display: true, text: 'Time of Day' }
            },
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Number of Interactions' }
            }
        },
        plugins: {
            tooltip: { enabled: true, mode: 'nearest', intersect: false },
            legend: { display: true, position: 'top' }
        }
    }
});
