const listDiv = document.getElementById("list");
const refreshBtn = document.getElementById("refresh");
const clearBtn = document.getElementById("clear");

function loadImages() {
  chrome.runtime.sendMessage({ action: "getImages" }, (response) => {
    listDiv.innerHTML = "";
    response.images.forEach((url) => {
      const item = document.createElement("div");
      item.className = "item";

      const img = document.createElement("img");
      img.src = url;
      img.className = "thumb";
      img.title = "Click to copy URL";
      img.onclick = () => {
        navigator.clipboard.writeText(url);
        img.style.opacity = "0.6";
        setTimeout(() => (img.style.opacity = "1"), 400);
      };

      const text = document.createElement("div");
      text.className = "url";
      text.textContent = url.split("/").pop().slice(0, 25); // shortened filename
      text.title = url;
      text.onclick = () => {
        navigator.clipboard.writeText(url);
        text.style.color = "#007aff";
        setTimeout(() => (text.style.color = ""), 500);
      };

      item.appendChild(img);
      item.appendChild(text);
      listDiv.appendChild(item);
    });
  });
}

refreshBtn.onclick = loadImages;
clearBtn.onclick = () => {
  chrome.runtime.sendMessage({ action: "clear" }, () => loadImages());
};

loadImages();
