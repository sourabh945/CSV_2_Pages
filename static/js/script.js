document.addEventListener("DOMContentLoaded", () => {
  // --- State Management ---
  let currentRowIndex = 0;
  let headers = [];

  // --- DOM Elements ---
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dataDisplay = document.getElementById("data-display");
  const rowCounter = document.getElementById("row-counter");
  const gotoPage = document.getElementById("goto");
  const gotoBtn = document.getElementById("goto-btn");

  // --- Core Function to Fetch and Display Data ---
  const fetchAndDisplayRow = async (index) => {
    dataDisplay.classList.add("loading");
    dataDisplay.innerHTML = "Loading data...";

    try {
      // Fetch both headers and row data
      const [headersRes, rowRes] = await Promise.all([
        // Only fetch headers if we don't have them yet
        headers.length === 0 ? fetch("/api/headers") : Promise.resolve(null),
        fetch(`/api/data/${index}`),
      ]);

      // Process headers if fetched
      if (headersRes && headersRes.ok) {
        headers = await headersRes.json();
      }

      // Check if the row data request was successful
      if (!rowRes.ok) {
        // This likely means we are at the end of the data
        throw new Error("End of data");
      }

      const rowData = await rowRes.json();

      // --- Update the UI ---
      dataDisplay.innerHTML = ""; // Clear the loading message
      dataDisplay.classList.remove("loading");

      // Create and append the data items
      headers.forEach((header, i) => {
        const dataItem = document.createElement("div");
        dataItem.className = "data-item";

        const headerSpan = document.createElement("span");
        headerSpan.className = "data-header";
        headerSpan.textContent = `${header}:`;

        const valueSpan = document.createElement("span");
        valueSpan.className = "data-value";
        valueSpan.textContent = rowData[i] || "N/A"; // Handle missing data

        dataItem.appendChild(headerSpan);
        dataItem.appendChild(valueSpan);
        dataDisplay.appendChild(dataItem);
      });

      // Update the current index state
      currentRowIndex = index;
    } catch (error) {
      // If we reach the end, show a message and disable the 'Next' button
      dataDisplay.innerHTML = "No more data available.";
      nextBtn.disabled = true;
    } finally {
      // Update the state of the buttons every time
      updateButtonStates();
    }
  };

  // --- Function to Update Button States ---
  const updateButtonStates = () => {
    // Disable 'Previous' if we are at the first row
    prevBtn.disabled = currentRowIndex <= 0;

    // Re-enable 'Next' button optimistically; it will be disabled by the fetch logic if needed
    if (!nextBtn.disabled) {
      // do nothing if already enabled
    } else if (error.message !== "End of data") {
      // only re-enable if not at end
      nextBtn.disabled = false;
    }

    rowCounter.textContent = `Row ${currentRowIndex + 1}`;
  };

  gotoPage.addEventListener("input", () => {
    gotoBtn.disabled =
      gotoPage.value === "" ||
      isNaN(gotoPage.value) ||
      parseInt(gotoPage.value) < 1;
  });

  gotoBtn.addEventListener("click", () => {
    const rowNumber = gotoPage.value;
    if (rowNumber) {
      fetchAndDisplayRow(parseInt(rowNumber - 1));
      gotoPage.value = "";
      gotoBtn.disabled = true;
    }
  });

  // --- Event Listeners ---
  nextBtn.addEventListener("click", () => {
    fetchAndDisplayRow(currentRowIndex + 1);
  });

  prevBtn.addEventListener("click", () => {
    // When we go back, the 'Next' row definitely exists, so re-enable the button
    nextBtn.disabled = false;
    if (currentRowIndex > 0) {
      fetchAndDisplayRow(currentRowIndex - 1);
    }
  });

  // --- Initial Load ---
  // Fetch the first row (index 0) when the page loads
  fetchAndDisplayRow(0);
});
