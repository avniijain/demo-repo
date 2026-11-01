const form = document.getElementById("bookmark-form");
const titleInput = document.getElementById("title");
const urlInput = document.getElementById("url");
const formMessage = document.getElementById("form-message");
const listMessage = document.getElementById("list-message");
const list = document.getElementById("bookmark-list");
const count = document.getElementById("bookmark-count");
const footerInfo = document.getElementById("footer-info");

function validWebUrl(value) {
  return value.startsWith("http://") || value.startsWith("https://");
}

function showEmptyState() {
  const item = document.createElement("li");
  item.className = "empty-state";
  item.textContent = "No bookmarks yet. Add a link above to get started.";
  list.appendChild(item);
}

function renderBookmarks(bookmarks) {
  list.replaceChildren();
  count.textContent = `${bookmarks.length} ${bookmarks.length === 1 ? "link" : "links"}`;
  if (bookmarks.length === 0) {
    showEmptyState();
    return;
  }

  bookmarks.forEach((bookmark) => {
    const item = document.createElement("li");
    item.className = "bookmark-item";
    const copy = document.createElement("div");
    copy.className = "bookmark-copy";
    const title = document.createElement("a");
    title.className = "bookmark-title";
    title.textContent = bookmark.title;
    if (validWebUrl(bookmark.url)) {
      title.href = bookmark.url;
      title.target = "_blank";
      title.rel = "noopener noreferrer";
    }
    const url = document.createElement("span");
    url.className = "bookmark-url";
    url.textContent = bookmark.url;
    copy.append(title, url);

    const remove = document.createElement("button");
    remove.className = "delete-button";
    remove.type = "button";
    remove.textContent = "Delete";
    remove.setAttribute("aria-label", `Delete ${bookmark.title}`);
    remove.addEventListener("click", () => deleteBookmark(bookmark.id));
    item.append(copy, remove);
    list.appendChild(item);
  });
}

async function loadBookmarks() {
  listMessage.textContent = "";
  try {
    const response = await fetch("/bookmarks");
    if (!response.ok) throw new Error("Could not load bookmarks.");
    renderBookmarks(await response.json());
  } catch (error) {
    list.replaceChildren();
    count.textContent = "";
    listMessage.textContent = "We couldn't load your bookmarks. Please try again.";
  }
}

async function deleteBookmark(id) {
  listMessage.textContent = "";
  try {
    const response = await fetch(`/bookmarks/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!response.ok) throw new Error("Could not delete bookmark.");
    await loadBookmarks();
  } catch (error) {
    listMessage.textContent = "We couldn't delete that bookmark. Please try again.";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "";
  const title = titleInput.value.trim();
  const url = urlInput.value.trim();
  if (!title || !validWebUrl(url)) {
    formMessage.textContent = "Enter a title and a URL beginning with http:// or https://.";
    return;
  }
  try {
    const response = await fetch("/bookmarks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, url }),
    });
    if (!response.ok) throw new Error("Could not save bookmark.");
    form.reset();
    await loadBookmarks();
  } catch (error) {
    formMessage.textContent = "We couldn't save that bookmark. Please check the details and try again.";
  }
});

async function loadInfo() {
  try {
    const response = await fetch("/info");
    if (!response.ok) throw new Error("Could not load deployment info.");
    const info = await response.json();
    footerInfo.textContent = `Deployed commit ${info.commit} - protected by CloudGuard`;
  } catch (error) {
    footerInfo.textContent = "Deployment info unavailable - protected by CloudGuard";
  }
}

loadBookmarks();
loadInfo();
