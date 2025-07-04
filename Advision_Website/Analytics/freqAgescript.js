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



 // Fetch frequent age-group data
async function fetchFrequentAgeGroups() {
    try {
        const response = await fetch("http://127.0.0.1:8000/analytics/frequent-age-groups");
        const data = await response.json();
        updateFreqAgeChart(data.frequent_age_groups);
    } catch (error) {
        console.error("Error fetching frequent age-group data:", error);
    }
}

// Update the chart with real backend data
function updateFreqAgeChart(data) {
    freqAgeChart.data.labels = Object.keys(data);
    freqAgeChart.data.datasets[0].data = Object.values(data);
    freqAgeChart.update();
}

// Initialize chart
const freqAgeChart = new Chart(document.getElementById('freqAgeChart'), {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Interactions',
            data: [],
            backgroundColor: '#4CAF50',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true }
        }
    }
});

// Fetch data when page loads
document.addEventListener("DOMContentLoaded", fetchFrequentAgeGroups);
