
function fetchLogs() {
    fetch("http://127.0.0.1:8000/get-logs")
        .then(response => response.json())
        .then(data => {
            displayLogs(data.logs);
        })
        .catch(error => console.error("Error fetching logs:", error));
}

function displayLogs(logs) {
    const tableBody = document.getElementById("tableBody");
    tableBody.innerHTML = ""; // Clear old data

    logs.forEach(log => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${log.log_id}</td>
            <td>${log.timestamp}</td>
            <td>${log.ad_id}</td>
            <td>${log.age_group}</td>
            <td>${log.gender}</td>
            <td>${log.final_mood}</td>
            <td>${log.switched_ad}</td>
        `;
        tableBody.appendChild(row);
    });
}

function searchTable() {
  let input = document.getElementById("searchInput").value.toLowerCase();
  let rows = document.querySelectorAll("#logsTable tbody tr");

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
  let table = document.getElementById("logsTable");
  let rows = Array.from(table.querySelectorAll("tbody tr"));
  
  // Filter out hidden rows
  let visibleRows = rows.filter(row => row.style.display !== "none");

  let sortedRows = visibleRows.sort((a, b) => {
      let cellA = a.cells[columnIndex].innerText;
      let cellB = b.cells[columnIndex].innerText;
      return cellA.localeCompare(cellB, undefined, { numeric: true });
  });

  // Append sorted visible rows to the table
  let tbody = table.querySelector("tbody");
  tbody.innerHTML = ""; // Clear the table body
  sortedRows.forEach(row => tbody.appendChild(row));
}

document.addEventListener("DOMContentLoaded", fetchLogs);
