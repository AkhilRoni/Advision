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

// Fetch Mood Trend Data from backend
//------------------------------------------------------------------------------------------
// Fetch Mood Trend Data from backend
// Fetch Mood Trend Data from backend
async function fetchMoodTrendData() {
    try {
        const response = await fetch("http://127.0.0.1:8000/analytics/mood-trend");
        const data = await response.json();
        updateMoodTrendChart(data);
    } catch (error) {
        console.error("Error fetching mood trend data:", error);
    }
}

// Update the Line Chart
function updateMoodTrendChart(data) {
    if (!data || Object.keys(data).length === 0) {
        console.log("No mood trend data found.");
        return;
    }

    const labels = data.hours.map(hour => parseInt(hour)); // Convert "00" to 0, "01" to 1, ..., "23" to 23
    const happyValues = data.happy;
    const angryValues = data.angry;
    const sadValues = data.sad;

    moodTrendChart.data.labels = labels;
    moodTrendChart.data.datasets[0].data = happyValues;
    moodTrendChart.data.datasets[1].data = angryValues;
    moodTrendChart.data.datasets[2].data = sadValues;
    moodTrendChart.update();
}

// Initialize Line Chart
const moodTrendChart = new Chart(document.getElementById("moodTrendChart"), {
    type: "line",
    data: {
        labels: [],
        datasets: [
            {
                label: "Happy",
                data: [],
                borderColor: "#4CAF50",
                backgroundColor: "rgba(76, 175, 80, 0.2)",
                fill: true
            },
            {
                label: "Angry",
                data: [],
                borderColor: "#F44336",
                backgroundColor: "rgba(244, 67, 54, 0.2)",
                fill: true
            },
            {
                label: "Sad",
                data: [],
                borderColor: "#03A9F4",
                backgroundColor: "rgba(3, 169, 244, 0.2)",
                fill: true
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: { display: true, text: "Hour of the Day" },
                ticks: {
                    stepSize: 1, // Ensure it shows every hour
                    callback: function (value, index, values) {
                        return value + ":00"; // Display as "0:00", "1:00", ..., "23:00"
                    }
                }
            },
            y: {
                beginAtZero: true,
                title: { display: true, text: "Average Mood Count" }
            }
        }
    }
    
});

// Fetch data on page load
document.addEventListener("DOMContentLoaded", fetchMoodTrendData);
