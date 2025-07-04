// sidebar.js

// Function to initialize the sidebar
function initializeSidebar() {
    const sidebar = document.querySelector(".sidebar");
    const sidebarToggler = document.querySelector(".sidebar-toggler");
    const menuToggler = document.querySelector(".menu-toggler");
    let collapsedSidebarHeight = "56px";
    let fullSidebarHeight = "calc(100vh - 32px)";
  
    // Toggle sidebar's collapsed state
    sidebarToggler.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
      updateDropdownVisibility();
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
    const dropdownToggle = document.querySelector(".nav-item.dropdown .nav-link");
    const dropdown = document.querySelector(".nav-item.dropdown");
    const dropdownList = dropdown.querySelector(".dropdown-list");
  
    dropdownToggle.addEventListener("click", function (e) {
      e.preventDefault();
      dropdown.classList.toggle("active");
      updateDropdownVisibility();
    });
  
    document.addEventListener("click", function (e) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("active");
        updateDropdownVisibility();
      }
    });
  
    function updateDropdownVisibility() {
      if (sidebar.classList.contains("collapsed")) {
        dropdownList.style.display = dropdown.classList.contains("active") ? "block" : "none";
      } else {
        dropdownList.style.display = dropdown.classList.contains("active") ? "block" : "none";
      }
    }
  }
  
  // Wait for the DOM to load, then initialize the sidebar
  document.addEventListener("DOMContentLoaded", () => {
    // Check if the sidebar is already in the DOM
    if (document.querySelector(".sidebar")) {
      initializeSidebar(); // Initialize immediately if sidebar is already loaded
    } else {
      // If the sidebar is being loaded dynamically, wait for it to be added to the DOM
      const observer = new MutationObserver((mutationsList, observer) => {
        for (let mutation of mutationsList) {
          if (mutation.type === "childList" && document.querySelector(".sidebar")) {
            initializeSidebar(); // Initialize when the sidebar is added
            observer.disconnect(); // Stop observing once the sidebar is found
            break;
          }
        }
      });
  
      // Start observing the document for changes
      observer.observe(document.body, { childList: true, subtree: true });
    }
  });