let imageUrls = [];

chrome.webRequest.onCompleted.addListener(
  (details) => {
    const url = details.url;
    if (url.match(/\.(jpg|jpeg|png|webp|gif)$/i)) {
      if (!imageUrls.includes(url)) {
        imageUrls.push(url);
        console.log("Captured:", url);
      }
    }
  },
  { urls: ["<all_urls>"] }
);

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "getImages") {
    sendResponse({ images: imageUrls });
  } else if (msg.action === "clear") {
    imageUrls = [];
    sendResponse({ cleared: true });
  }
});
