/**
 * Discover Pakistan — Litquidity-Style Editorial Blog Engine
 */

let allPosts = [];
let currentCategory = "All";
let searchQuery = "";

const featuredSlot = document.getElementById("featured-story-slot");
const stackSlot = document.getElementById("stacked-stories-slot");
const editorialGrid = document.getElementById("editorial-grid");
const filterPillsContainer = document.getElementById("filter-pills");
const searchInput = document.getElementById("search-input");
const themeToggleBtn = document.getElementById("theme-toggle-btn");
const readerModal = document.getElementById("reader-modal");
const modalCloseBtn = document.getElementById("modal-close-btn");

document.addEventListener("DOMContentLoaded", async () => {
  initTheme();
  await loadPosts();
  initCategoryFilters();
  initSearch();
  initModalListeners();
  checkUrlHash();
});

async function loadPosts() {
  try {
    const res = await fetch("posts.json?t=" + Date.now());
    if (res.ok) {
      allPosts = await res.json();
    } else {
      throw new Error("HTTP error " + res.status);
    }
  } catch (err) {
    console.warn("Could not fetch posts.json dynamically. Using inline data:", err);
    if (window.INITIAL_POSTS && Array.isArray(window.INITIAL_POSTS)) {
      allPosts = window.INITIAL_POSTS;
    }
  }
  renderAll();
}

function renderAll() {
  renderHeroSection();
  renderGridSection();
}

function renderHeroSection() {
  if (!allPosts || allPosts.length === 0) return;

  const filtered = getFilteredPosts();
  if (filtered.length === 0) {
    featuredSlot.innerHTML = `<div class="p-8 text-center text-muted">No travel dossiers found matching "${searchQuery}".</div>`;
    stackSlot.innerHTML = "";
    return;
  }

  const leadPost = filtered[0];
  featuredSlot.innerHTML = `
    <div class="featured-lead-card" onclick="openArticleModal('${leadPost.id}')">
      <div class="featured-media-wrapper">
        <img class="featured-media-img" src="${leadPost.image}" alt="${escapeHtml(leadPost.title)}" loading="lazy" />
        <span class="media-badge">${escapeHtml(leadPost.badge || leadPost.category)}</span>
        ${leadPost.stat_number ? `
          <div class="stat-chip">
            <span class="stat-chip-num">${escapeHtml(leadPost.stat_number)}</span>
            <span class="stat-chip-label">${escapeHtml(leadPost.stat_label || "METRIC")}</span>
          </div>
        ` : ''}
      </div>
      <h2 class="featured-title">${escapeHtml(leadPost.title)}</h2>
      <p class="featured-subdeck">${escapeHtml(leadPost.subdeck)}</p>
      <div class="author-meta-row">
        <img class="author-avatar" src="${leadPost.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(leadPost.author)}" />
        <span class="author-name">${escapeHtml(leadPost.author || "Travel Desk")}</span>
        <span class="meta-separator">•</span>
        <span class="meta-date">${escapeHtml(leadPost.date)}</span>
        <span class="meta-separator">•</span>
        <span class="meta-date">${escapeHtml(leadPost.read_time || "5 min read")}</span>
      </div>
    </div>
  `;

  const stackPosts = filtered.slice(1, 4);
  stackSlot.innerHTML = stackPosts.map(post => `
    <div class="stacked-story-card" onclick="openArticleModal('${post.id}')">
      <div class="stacked-thumb-wrapper">
        <img class="stacked-thumb-img" src="${post.image}" alt="${escapeHtml(post.title)}" loading="lazy" />
      </div>
      <div class="stacked-story-info">
        <h3 class="stacked-story-title">${escapeHtml(post.title)}</h3>
        <p class="stacked-story-excerpt">${escapeHtml(post.subdeck)}</p>
        <div class="author-meta-row">
          <img class="author-avatar" src="${post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(post.author)}" />
          <span class="author-name">${escapeHtml(post.author || "Travel Desk")}</span>
          <span class="meta-separator">•</span>
          <span class="meta-date">${escapeHtml(post.date)}</span>
        </div>
      </div>
    </div>
  `).join("");
}

function renderGridSection() {
  const filtered = getFilteredPosts();
  const gridPosts = (currentCategory === "All" && !searchQuery) ? filtered.slice(4) : filtered;

  if (gridPosts.length === 0) {
    editorialGrid.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 48px; text-align: center; color: var(--text-muted);">
        <p style="font-size: 1.1rem; margin-bottom: 8px;">No additional travel dossiers in this category.</p>
        <button class="pill-btn active" onclick="setCategory('All')">View All Expeditions</button>
      </div>
    `;
    return;
  }

  editorialGrid.innerHTML = gridPosts.map(post => `
    <div class="editorial-card" onclick="openArticleModal('${post.id}')">
      <div class="editorial-card-thumb">
        <img class="editorial-card-img" src="${post.image}" alt="${escapeHtml(post.title)}" loading="lazy" />
        ${post.badge ? `<span class="media-badge">${escapeHtml(post.badge)}</span>` : ''}
      </div>
      <div class="card-category-tag">${escapeHtml(post.category)}</div>
      <h3 class="editorial-card-title">${escapeHtml(post.title)}</h3>
      <p class="editorial-card-excerpt">${escapeHtml(post.subdeck)}</p>
      <div class="author-meta-row">
        <img class="author-avatar" src="${post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(post.author)}" />
        <span class="author-name">${escapeHtml(post.author)}</span>
        <span class="meta-separator">•</span>
        <span class="meta-date">${escapeHtml(post.date)}</span>
      </div>
    </div>
  `).join("");
}

function getFilteredPosts() {
  return allPosts.filter(post => {
    const matchesCat = (currentCategory === "All") || (post.category.toLowerCase() === currentCategory.toLowerCase());
    if (!matchesCat) return false;

    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const titleMatch = post.title.toLowerCase().includes(q);
    const subdeckMatch = post.subdeck && post.subdeck.toLowerCase().includes(q);
    const categoryMatch = post.category && post.category.toLowerCase().includes(q);
    return titleMatch || subdeckMatch || categoryMatch;
  });
}

function initCategoryFilters() {
  const categories = ["All", "Alpine Expeditions", "Wilderness Expeditions", "Travel Itineraries", "Cultural Heritage", "Coastal & Desert"];
  filterPillsContainer.innerHTML = categories.map(cat => `
    <button class="pill-btn ${cat === currentCategory ? 'active' : ''}" onclick="setCategory('${cat}')">
      ${cat}
    </button>
  `).join("");
}

window.setCategory = function(cat) {
  currentCategory = cat;
  document.querySelectorAll(".pill-btn").forEach(btn => {
    btn.classList.toggle("active", btn.textContent.trim() === cat);
  });
  renderAll();
};

function initSearch() {
  if (!searchInput) return;
  searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value.trim();
    renderAll();
  });
}

window.openArticleModal = function(id) {
  const post = allPosts.find(p => p.id === id);
  if (!post) return;

  const modalCategory = document.getElementById("modal-category");
  const modalDate = document.getElementById("modal-date");
  const modalTitle = document.getElementById("modal-title");
  const modalSubdeck = document.getElementById("modal-subdeck");
  const modalAuthorAvatar = document.getElementById("modal-author-avatar");
  const modalAuthorName = document.getElementById("modal-author-name");
  const modalReadTime = document.getElementById("modal-read-time");
  const modalHeroImg = document.getElementById("modal-hero-img");
  const modalStatBox = document.getElementById("modal-stat-box");
  const modalStatValue = document.getElementById("modal-stat-value");
  const modalStatText = document.getElementById("modal-stat-text");
  const modalBodyProse = document.getElementById("modal-body-prose");
  const modalTakeawaysCard = document.getElementById("modal-takeaways-card");
  const modalTakeawaysList = document.getElementById("modal-takeaways-list");

  modalCategory.textContent = post.badge || post.category;
  modalDate.textContent = post.date;
  modalTitle.textContent = post.title;
  modalSubdeck.textContent = post.subdeck;
  modalAuthorAvatar.src = post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop';
  modalAuthorName.textContent = post.author || "Travel Desk";
  modalReadTime.textContent = post.read_time || "5 min read";
  modalHeroImg.src = post.image;
  modalHeroImg.alt = post.title;

  if (post.stat_number) {
    modalStatBox.style.display = "flex";
    modalStatValue.textContent = post.stat_number;
    modalStatText.textContent = (post.stat_label || "KEY METRIC") + ": " + (post.subdeck || "");
  } else {
    modalStatBox.style.display = "none";
  }

  if (Array.isArray(post.body)) {
    modalBodyProse.innerHTML = post.body.map(para => `<p>${escapeHtml(para)}</p>`).join("");
  } else if (typeof post.body === "string") {
    modalBodyProse.innerHTML = `<p>${escapeHtml(post.body)}</p>`;
  } else {
    modalBodyProse.innerHTML = `<p>${escapeHtml(post.subdeck)}</p>`;
  }

  if (post.takeaways && post.takeaways.length > 0) {
    modalTakeawaysCard.style.display = "block";
    modalTakeawaysList.innerHTML = post.takeaways.map(t => `<li>${escapeHtml(t)}</li>`).join("");
  } else {
    modalTakeawaysCard.style.display = "none";
  }

  readerModal.classList.add("open");
  document.body.style.overflow = "hidden";
  window.location.hash = post.id;
};

window.closeArticleModal = function() {
  readerModal.classList.remove("open");
  document.body.style.overflow = "";
  history.replaceState(null, null, ' ');
};

function initModalListeners() {
  modalCloseBtn.addEventListener("click", closeArticleModal);
  readerModal.addEventListener("click", (e) => {
    if (e.target === readerModal) {
      closeArticleModal();
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && readerModal.classList.contains("open")) {
      closeArticleModal();
    }
  });
}

function checkUrlHash() {
  const hash = window.location.hash.replace("#", "");
  if (hash) {
    setTimeout(() => openArticleModal(hash), 300);
  }
}

function initTheme() {
  const saved = localStorage.getItem("dp_theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon(saved);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("dp_theme", next);
      updateThemeIcon(next);
    });
  }
}

function updateThemeIcon(theme) {
  if (!themeToggleBtn) return;
  themeToggleBtn.innerHTML = theme === "dark" 
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
}

window.shareStory = function(platform) {
  const url = window.location.href;
  const title = document.getElementById("modal-title").textContent;
  if (platform === "twitter") {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`, "_blank");
  } else if (platform === "facebook") {
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, "_blank");
  } else if (platform === "copy") {
    navigator.clipboard.writeText(url).then(() => {
      alert("Travel dossier link copied to clipboard!");
    });
  }
};

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
