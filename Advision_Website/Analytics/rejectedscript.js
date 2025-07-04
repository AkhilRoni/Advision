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

// Fetch rejected ads data from backend
// Fetch rejected ads data from backend
async function fetchRejectedAds() {
    try {
        const response = await fetch("http://127.0.0.1:8000/analytics/rejected-ads");
        const data = await response.json();
        updateRejectedAdsChart(data.rejected_ads);
    } catch (error) {
        console.error("Error fetching rejected ads data:", error);
    }
}

// Update the rejected ads chart
function updateRejectedAdsChart(data) {
    if (!data || data.length === 0) {
        console.log("No rejected ads data found.");
        return;
    }

    const labels = data.map(ad => `${ad.ad_name} (${ad.age_group})`);
    const values = data.map(ad => ad.rejections);

    rejectedAdsChart.data.labels = labels;
    rejectedAdsChart.data.datasets[0].data = values;
    rejectedAdsChart.update();
}

// Initialize chart with empty data
const rejectedAdsChart = new Chart(document.getElementById('rejectedAdsChart'), {
    type: 'pie',
    data: {
        labels: [],
        datasets: [{
            label: 'Rejections',
            data: [],
            backgroundColor: [
                '#F44336', // Red
                '#4CAF50', // Green
                '#2196F3', // Blue
                '#FFEB3B', // Yellow
                '#673AB7', // Deep Purple
                '#FF9800', // Orange
                '#795548', // Brown
                '#3F51B5', // Indigo
                '#00E676', // Bright Green

                '#448AFF', // Light Blue
                '#C2185B', // Crimson
                '#7C4DFF', // Vivid Purple
                '#FF4081', // Hot Pink
                '#76FF03', // Neon Green
                '#F57C00', // Deep Orange
            ]
            
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Fetch data on page load
document.addEventListener("DOMContentLoaded", fetchRejectedAds);
