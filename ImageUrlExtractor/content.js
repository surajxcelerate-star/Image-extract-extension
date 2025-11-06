// content.js
window.imageUrls = [];

// Get highest-res URL from <img>
function getHighestResImage(img) {
  if (!img) return null;
  if (img.srcset) {
    const sources = img.srcset.split(",").map((s) => s.trim());
    const lastSource = sources[sources.length - 1];
    return lastSource.split(" ")[0]; // URL only
  }
  return img.src;
}

// Capture all images
function captureImages() {
  document.querySelectorAll("img").forEach((img) => {
    const url = getHighestResImage(img);
    if (url && !window.imageUrls.includes(url)) {
      window.imageUrls.push(url);
      console.log("Captured:", url);
    }
  });
}

// Initial capture
captureImages();

// Observe dynamic content
const observer = new MutationObserver(() => captureImages());
observer.observe(document.body, { childList: true, subtree: true });

// Listen for popup messages
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "getImages") {
    sendResponse({ images: window.imageUrls });
  } else if (msg.action === "clear") {
    window.imageUrls = [];
    sendResponse({ cleared: true });
  }
});
