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
        dropdown.classList.toggle("active");
        updateDropdownVisibility();
        if (sidebar.classList.contains("collapsed")) {
            const dropdownList = dropdown.querySelector(".dropdown-list");
            if (dropdown.classList.contains("active")) {
                dropdownList.style.display = "block";
            } else {
                dropdownList.style.display = "none";
            }
        }
    });
    document.addEventListener("click", function (e) {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove("active");
            updateDropdownVisibility();
        }
    });
    function updateDropdownVisibility() {
        if (sidebar.classList.contains("collapsed")) {
            if (dropdown.classList.contains("active")) {
                dropdownList.style.display = "block";
            } else {
                dropdownList.style.display = "none";
            }
        } else {
            dropdownList.style.display = dropdown.classList.contains("active") ? "block" : "none";
        }
    }
});
//--------------------------------------------------------------------------------------------------

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


const freqAgeChart = new Chart(document.getElementById('freqAgeChart'), {
    type: 'bar',
    data: {
        labels: ['0-17', '18-30', '31-50', '51-70', '70+'],
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
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: "Frequent Age Group Interactions",
                font: { size: 16},
                color: "#423e3e"
            }
        },
        scales: {
            y: { beginAtZero: true }
        }
    }
});


// Fetch data when page loads
document.addEventListener("DOMContentLoaded", fetchFrequentAgeGroups);


//--------------------------------------------------------------------------------------------------

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
        labels: ['Ad 1', 'Ad 2', 'Ad 3', 'Ad 4', 'Ad 5'],
        datasets: [{
            label: 'Likes',
            data: [60, 90, 40, 70, 100],
            backgroundColor: ['#FFC107', '#03A9F4', '#E91E63', '#8BC34A', '#FF5722']
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: "Most Liked Ads",
                font: { size: 16},
                color: "#423e3e"
            }
        }
    }
});

document.addEventListener("DOMContentLoaded", fetchLikedAds);

//------------------------------------------------------------------------------------------

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


const rejectedAdsChart = new Chart(document.getElementById('rejectedAdsChart'), {
    type: 'pie',
    data: {
        labels: ['Ad 1', 'Ad 2', 'Ad 3', 'Ad 4', 'Ad 5'],
        datasets: [{
            label: 'Rejections',
            data: [80, 50, 120, 40, 30],
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
        },
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: "Most Rejected Ads",
                font: { size: 16 },
                color: "#423e3e"
            }
        }
    }
});

document.addEventListener("DOMContentLoaded", fetchRejectedAds);

//-------------------------------------------------------------------------------------
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
const timedistChart = new Chart(document.getElementById('timedistChart'), {
    type: 'line',
    data: {
        labels: ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM'],
        datasets: [{
            label: 'Interactions',
            data: [5, 3, 2, 4, 8, 6, 10, 15, 20, 30, 25, 28, 40, 35, 32, 20, 18, 22, 25, 27, 30, 15, 10, 8],
            backgroundColor: 'rgba(33, 150, 243, 0.2)',
            borderColor: '#2196F3',
            borderWidth: 2,
            pointBackgroundColor: '#2196F3',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#FF5722',
            pointHoverBorderColor: '#FF5722',
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: "Ad Interactions Over Time",
                font: { size: 16 },
                color: "#423e3e"
            }
        }
    }
});
//-------------------------------------------------------------------------------------------------
async function fetchAdSwitchData() {
    try {
        const response = await fetch("http://127.0.0.1:8000/analytics/ad-switch-ratio"); // Endpoint for switch ratio
        const data = await response.json();
        updateAdSwitchChart(data);
    } catch (error) {
        console.error("Error fetching ad switch data:", error);
    }
}

// Update the Pie Chart
function updateAdSwitchChart(data) {
    if (!data || Object.keys(data).length === 0) {
        console.log("No ad switch data found.");
        return;
    }

    const labels = ["Accepted Ads", "Rejected Ads"];
    const values = [data.switched, data.not_switched];

    adSwitchChart.data.labels = labels;
    adSwitchChart.data.datasets[0].data = values;
    adSwitchChart.update();
}

// Initialize Pie Chart
const adSwitchChart = new Chart(document.getElementById("adSwitchChart"), {
    type: "pie",
    data: {
        labels: [],
        datasets: [{
            label: "Ad Switch Ratio",
            data: [],
            backgroundColor: ["#FF5722", "#4CAF50"]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
                title: {
                    display: true,
                    text: "Ad Rejection Ratio",
                    font: { size: 16 },
                    color: "#423e3e"
                }
            }
    }
});

// Fetch data on page load
document.addEventListener("DOMContentLoaded", fetchAdSwitchData);

//------------------------------------------------------------------------------------------

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
        plugins: {
            legend: { display: false },
                title: {
                    display: true,
                    text: "Mood Trends over Time",
                    font: { size: 16 },
                    color: "#423e3e"
                }
            },
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

//---------------------------------------------------------------------------------------------------