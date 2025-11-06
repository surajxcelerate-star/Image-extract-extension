const list = document.getElementById("list");
const refreshBtn = document.getElementById("refresh");
const clearBtn = document.getElementById("clear");

// Render images in popup
function renderImages(images) {
  list.innerHTML = "";
  images.forEach((url) => {
    const div = document.createElement("div");
    div.className = "item";

    const img = document.createElement("img");
    img.src = url;
    img.className = "thumb";
    img.title = url;
    img.addEventListener("click", () => window.open(url, "_blank"));

    const span = document.createElement("span");
    span.className = "url";
    span.textContent = url;
    span.addEventListener("click", () => {
      navigator.clipboard.writeText(url);
      span.textContent = "Copied!";
      setTimeout(() => (span.textContent = url), 1000);
    });

    div.appendChild(img);
    div.appendChild(span);
    list.appendChild(div);
  });
}

// Fetch images from content script
function fetchImages() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        func: () => window.imageUrls || [],
      },
      (results) => {
        if (results && results[0] && results[0].result) {
          renderImages(results[0].result);
        }
      }
    );
  });
}

// Clear images
clearBtn.addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        func: () => {
          window.imageUrls = [];
          return true;
        },
      },
      () => fetchImages()
    );
  });
});

// Refresh images
refreshBtn.addEventListener("click", fetchImages);

// Initial load
fetchImages();
