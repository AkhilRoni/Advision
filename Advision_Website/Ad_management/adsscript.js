function fetchAds() {
    fetch("http://127.0.0.1:8000/get-all-ads")
        .then(response => response.json())
        .then(data => {
            displayAds(data.ads);
        })
        .catch(error => console.error("Error fetching ads:", error));
}

function displayAds(ads) {
    const tableBody = document.getElementById("tableBody");
    tableBody.innerHTML = ""; // Clear old data

    ads.forEach(ad => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${ad.ad_id}</td>
            <td>${ad.ad_name}</td>
            <td>${ad.age_group}</td>
            <td>${ad.gender}</td>
            <td>${ad.priority}</td>
            <td>${ad.file_path}</td>
        `;
        tableBody.appendChild(row);
    });
}

function searchTable() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let rows = document.querySelectorAll("#adsTable tbody tr");
  
    if (input === "") {
        rows.forEach(row => row.style.display = "");
        return;
    }
  
    rows.forEach(row => {
        let cells = row.querySelectorAll("td");
        let matchFound = false;
        cells.forEach(cell => {
            if (cell.innerText.toLowerCase() === input) {
                matchFound = true;
            }
        });
        row.style.display = matchFound ? "" : "none";
    });
}

function sortTable(columnIndex) {
    let table = document.getElementById("adsTable");
    let rows = Array.from(table.querySelectorAll("tbody tr"));
    let sortedRows = rows.sort((a, b) => {
        let cellA = a.cells[columnIndex].innerText;
        let cellB = b.cells[columnIndex].innerText;
        return cellA.localeCompare(cellB, undefined, { numeric: true });
    });
    
    let tbody = table.querySelector("tbody");
    tbody.innerHTML = "";
    sortedRows.forEach(row => tbody.appendChild(row));
}

document.addEventListener("DOMContentLoaded", fetchAds);
