


// Handle Ad Upload
const adForm = document.getElementById("adForm");
adForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append("ad_name", document.getElementById("adName").value);
    formData.append("ad_video", document.getElementById("adVideo").files[0]);
    formData.append("ad_gender", document.getElementById("gender").value);
    formData.append("ad_age", document.getElementById("ageGroup").value);

    try {
        const response = await fetch("http://127.0.0.1:8000/upload-ad", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        if (response.ok) {
            alert("Ad uploaded successfully!");
            adForm.reset();
        } else {
            alert("Failed to upload ad: " + data.detail);
        }
    } catch (error) {
        console.error("Error uploading ad:", error);
        alert("An error occurred while uploading the ad.");
    }
});
