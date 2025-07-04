
//------------------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function() {
  let selectedGender = null;
  let selectedAge = null;

  // Event listeners for gender buttons
  document.querySelectorAll('.gender-btn').forEach(button => {
    button.addEventListener('click', function() {
      selectedGender = this.getAttribute('data-gender');
      document.querySelectorAll('.gender-btn').forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Event listeners for age buttons
  document.querySelectorAll('.age-btn').forEach(button => {
    button.addEventListener('click', function() {
      selectedAge = this.getAttribute('data-age');
      document.querySelectorAll('.age-btn').forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Event listener for the submit button
  document.querySelector('.submit').addEventListener('click', function() {
    if (!selectedGender || !selectedAge) {
      alert('Please select both gender and age group.');
      return;
    }

    // Fetch and display ads based on selected criteria
    fetchAndDisplayAds(selectedGender, selectedAge);
  });

  // Function to fetch and display ads
  async function fetchAndDisplayAds(selectedGender, selectedAge) {
    try {
      const response = await fetch(`http://localhost:8000/get-ads?gender=${encodeURIComponent(selectedGender)}&age_group=${encodeURIComponent(selectedAge)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch ads');
      }
      const data = await response.json();
      displayAds(data.ads);
    } catch (error) {
      console.error('Error fetching ads:', error);
      const adsContainer = document.getElementById('adsContainer');
      adsContainer.innerHTML = '<p style="color: white;">Error fetching ads. Please try again later.</p>';
    }
  }

  // Function to display ads
  function displayAds(ads) {
    const adsContainer = document.getElementById('adsContainer');
    adsContainer.innerHTML = ''; // Clear previous ads

    if (ads.length === 0) {
      adsContainer.innerHTML = '<p style="color: white;">No ads found for the selected criteria.</p>';
      return;
    }

    ads.forEach(ad => {
      const adElement = document.createElement('div');
      adElement.classList.add('ad');
      adElement.id = `ad-${ad.ad_id}`; // Add an ID to the ad element
      adElement.innerHTML = `
        <div class="ad-info">
          <p><strong>ID:</strong> ${ad.ad_id}</p>
          <p><strong>Title:</strong> ${ad.ad_name}</p>
        </div>
        <button class="remove-btn" data-id="${ad.ad_id}">Remove</button>
      `;
      adsContainer.appendChild(adElement);
    });

    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-btn').forEach(button => {
      button.addEventListener('click', function() {
        const adId = parseInt(this.getAttribute('data-id'));
        removeAd(adId);
      });
    });
  }

  // Function to remove an ad
  function removeAd(adId) {
      console.log("Trying to delete ad with ID:", adId); // Debugging
      
      fetch(`http://127.0.0.1:8000/delete-ad/${adId}`, {
          method: "DELETE",  // 👈 THIS IS IMPORTANT!
          headers: {
              "Content-Type": "application/json",
          },
      })
      .then(response => {
          if (!response.ok) throw new Error("Failed to delete ad");
          return response.json();
      })
      .then(data => {
          console.log(data);
          document.getElementById(`ad-${adId}`).remove();
          console.log(`Ad ${adId} removed from UI.`);
      })
      .catch(error => console.error("Error deleting ad:", error));
  }

});