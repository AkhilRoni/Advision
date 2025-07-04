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

//-----------------------------------------------------------------------------------


async function fetchLikedAds() {
    try {
        const response = await fetch("http://127.0.0.1:8000/analytics/liked-ads");
        const data = await response.json();
        console.log("Fetched Liked Ads Data:", data.liked_ads); // Debugging line
        updateLikedAdsChart(data.liked_ads);
    } catch (error) {
        console.error("Error fetching liked ads data:", error);
    }
}

function updateLikedAdsChart(data) {
    if (!data || data.length === 0) {
        console.log("No liked ads data found.");
        return;
    }

    const labels = data.map(ad => `${ad.ad_name} (${ad.age_group})`); // Keep the same
    const values = data.map(ad => ad.likes); // FIX: Use `likes` instead of `rejections`

    likedAdsChart.data.labels = labels;
    likedAdsChart.data.datasets[0].data = values;
    likedAdsChart.update();
}


const likedAdsChart = new Chart(document.getElementById('likedAdsChart'), {
    type: 'doughnut',
    data: {
        labels: [],
        datasets: [{
            label: 'Likes',
            data: [], 
            backgroundColor: ['#FFC107', '#03A9F4', '#E91E63', '#8BC34A', '#FF5722']
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false, // Disable aspect ratio to customize size
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

document.addEventListener("DOMContentLoaded", fetchLikedAds);

