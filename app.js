/**
 * discover pakistan — Litquidity-Style Editorial Blog Engine
 */

let allPosts = window.INITIAL_POSTS || [];
let currentCategory = "All";
let searchQuery = "";
let articleStartTime = null;

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
  initCategoryFilters();
  initSearch();
  initModalListeners();
  
  // Reconcile with latest posts.json dynamically so newly added posts are always present
  await loadPosts();
  checkUrlHash();
  initWebVitalsObservability();
});

async function loadPosts() {
  try {
    const res = await fetch("posts.json?t=" + Date.now());
    if (res.ok) {
      const freshPosts = await res.json();
      if (Array.isArray(freshPosts) && freshPosts.length > 0) {
        allPosts = freshPosts;
      }
    }
  } catch (err) {
    console.warn("Could not fetch posts.json dynamically. Using inline data:", err);
  }
  renderAll();
}

function openMobileDrawer() {
  const drawer = document.getElementById("mobile-nav-drawer");
  const backdrop = document.getElementById("mobile-drawer-backdrop");
  if (drawer && backdrop) {
    drawer.style.display = "flex";
    backdrop.style.display = "block";
    drawer.classList.add("open");
    backdrop.classList.add("open");
    document.body.style.overflow = "hidden";
  }
}

function closeMobileDrawer() {
  const drawer = document.getElementById("mobile-nav-drawer");
  const backdrop = document.getElementById("mobile-drawer-backdrop");
  if (drawer && backdrop) {
    drawer.style.display = "none";
    backdrop.style.display = "none";
    drawer.classList.remove("open");
    backdrop.classList.remove("open");
    document.body.style.overflow = "";
  }
}

function renderAll() {
  renderHeroSection();
  renderGridSection();
}

function renderHeroSection() {
  if (!allPosts || allPosts.length === 0) return;

  const filtered = getFilteredPosts();
  if (filtered.length === 0) {
    featuredSlot.innerHTML = `<div style="padding: 48px; text-align: center; color: var(--text-muted);">No stories found matching "${escapeHtml(searchQuery)}".</div>`;
    stackSlot.innerHTML = "";
    return;
  }

  const leadPost = filtered[0];
  const isLeadUrdu = leadPost.lang === 'ur' || /[؀-ۿ]/.test(leadPost.title || "");
  const leadTitleCls = isLeadUrdu ? "featured-title urdu-title" : "featured-title";
  const leadSubdeckCls = isLeadUrdu ? "featured-subdeck urdu-subdeck" : "featured-subdeck";

  featuredSlot.innerHTML = `
    <a href="posts/${leadPost.id}/" class="featured-lead-card" onclick="openArticleModal('${leadPost.id}'); return false;">
      <div class="featured-media-wrapper">
        <img class="featured-media-img" src="${leadPost.image}" alt="${escapeHtml(leadPost.title)}" width="1200" height="675" loading="eager" fetchpriority="high" decoding="async" />
        <span class="media-badge">${escapeHtml(leadPost.badge || leadPost.category)}</span>
        ${leadPost.stat_number ? `
          <div class="stat-chip">
            <span class="stat-chip-num">${escapeHtml(leadPost.stat_number)}</span>
            <span class="stat-chip-label">${escapeHtml(leadPost.stat_label || "KEY METRIC")}</span>
          </div>
        ` : ''}
      </div>
      <h2 class="${leadTitleCls}" ${isLeadUrdu ? 'dir="rtl"' : ''}>${escapeHtml(leadPost.title)}</h2>
      <p class="${leadSubdeckCls}" ${isLeadUrdu ? 'dir="rtl"' : ''}>${escapeHtml(leadPost.subdeck)}</p>
      <div class="author-meta-row">
        <img class="author-avatar" src="${leadPost.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(leadPost.author || 'Kamran Alvi')}" width="28" height="28" loading="lazy" decoding="async" />
        <span class="author-name">${escapeHtml(leadPost.author || "Kamran Alvi")}</span>
        <span class="meta-separator">•</span>
        <span class="meta-date">${escapeHtml(leadPost.date)}</span>
        <span class="meta-separator">•</span>
        <span class="meta-date">${escapeHtml(leadPost.read_time || "4 min read")}</span>
      </div>
    </a>
  `;

  const stackPosts = filtered.slice(1, 4);
  stackSlot.innerHTML = stackPosts.map(post => {
    const isUrdu = post.lang === 'ur' || /[؀-ۿ]/.test(post.title || "");
    const titleCls = isUrdu ? "stacked-story-title urdu-title" : "stacked-story-title";
    const subdeckCls = isUrdu ? "stacked-story-excerpt urdu-subdeck" : "stacked-story-excerpt";
    return `
    <a href="posts/${post.id}/" class="stacked-story-card" onclick="openArticleModal('${post.id}'); return false;">
      <div class="stacked-thumb-wrapper">
        <img class="stacked-thumb-img" src="${post.image}" alt="${escapeHtml(post.title)}" width="480" height="270" loading="lazy" decoding="async" />
      </div>
      <div class="stacked-story-info">
        <h3 class="${titleCls}" ${isUrdu ? 'dir="rtl"' : ''}>${escapeHtml(post.title)}</h3>
        <p class="${subdeckCls}" ${isUrdu ? 'dir="rtl"' : ''}>${escapeHtml(post.subdeck)}</p>
        <div class="author-meta-row">
          <img class="author-avatar" src="${post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(post.author || 'Kamran Alvi')}" width="24" height="24" loading="lazy" decoding="async" />
          <span class="author-name">${escapeHtml(post.author || "Kamran Alvi")}</span>
          <span class="meta-separator">•</span>
          <span class="meta-date">${escapeHtml(post.date)}</span>
        </div>
      </div>
    </a>
  `}).join("");
}

function renderGridSection() {
  const filtered = getFilteredPosts();
  const gridPosts = (currentCategory === "All" && !searchQuery) ? filtered.slice(4) : filtered;

  if (gridPosts.length === 0) {
    editorialGrid.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 48px; text-align: center; color: var(--text-muted);">
        <p style="font-size: 1.1rem; margin-bottom: 8px;">No additional stories in this category.</p>
        <button class="pill-btn active" onclick="setCategory('All')">View All Stories</button>
      </div>
    `;
    return;
  }

  editorialGrid.innerHTML = gridPosts.map(post => {
    const isUrdu = post.lang === 'ur' || /[؀-ۿ]/.test(post.title || "");
    const titleCls = isUrdu ? "editorial-card-title urdu-title" : "editorial-card-title";
    const subdeckCls = isUrdu ? "editorial-card-excerpt urdu-subdeck" : "editorial-card-excerpt";
    return `
    <a href="posts/${post.id}/" class="editorial-card" onclick="openArticleModal('${post.id}'); return false;">
      <div class="editorial-card-thumb">
        <img class="editorial-card-img" src="${post.image}" alt="${escapeHtml(post.title)}" width="600" height="338" loading="lazy" decoding="async" />
        ${post.badge ? `<span class="media-badge">${escapeHtml(post.badge)}</span>` : ''}
      </div>
      <div class="card-category-tag">${escapeHtml(post.category)}</div>
      <h3 class="${titleCls}" ${isUrdu ? 'dir="rtl"' : ''}>${escapeHtml(post.title)}</h3>
      <p class="${subdeckCls}" ${isUrdu ? 'dir="rtl"' : ''}>${escapeHtml(post.subdeck)}</p>
      <div class="author-meta-row">
        <img class="author-avatar" src="${post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(post.author || 'Kamran Alvi')}" width="24" height="24" loading="lazy" decoding="async" />
        <span class="author-name">${escapeHtml(post.author || "Kamran Alvi")}</span>
        <span class="meta-separator">•</span>
        <span class="meta-date">${escapeHtml(post.date)}</span>
      </div>
    </a>
  `}).join("");
}

function getFilteredPosts() {
  return allPosts.filter(post => {
    const matchesCat = (currentCategory === "All") || (post.category && post.category.toLowerCase() === currentCategory.toLowerCase());
    if (!matchesCat) return false;

    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    const titleMatch = post.title && post.title.toLowerCase().includes(q);
    const subdeckMatch = post.subdeck && post.subdeck.toLowerCase().includes(q);
    const categoryMatch = post.category && post.category.toLowerCase().includes(q);
    return titleMatch || subdeckMatch || categoryMatch;
  });
}

function initCategoryFilters() {
  if (!filterPillsContainer) return;
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

window.openArticleModal = async function(id) {
  let post = allPosts.find(p => p.id === id);
  if (!post) {
    try {
      const res = await fetch("posts.json?t=" + Date.now());
      if (res.ok) {
        allPosts = await res.json();
        post = allPosts.find(p => p.id === id);
      }
    } catch (e) {
      console.error("Could not fetch posts.json dynamically:", e);
    }
  }

  if (!post) {
    console.warn("Post not found:", id);
    return;
  }

  articleStartTime = Date.now();

  const modalCategory = document.getElementById("modal-category");
  const modalDate = document.getElementById("modal-date");
  const modalTitle = document.getElementById("modal-title");
  const modalSubdeck = document.getElementById("modal-subdeck");
  const modalAuthorAvatar = document.getElementById("modal-author-avatar");
  const modalAuthorName = document.getElementById("modal-author-name");
  const modalAuthorRole = document.getElementById("modal-author-role");
  const modalReadTime = document.getElementById("modal-read-time");
  const modalHeroImg = document.getElementById("modal-hero-img");
  const modalStatBox = document.getElementById("modal-stat-box");
  const modalStatValue = document.getElementById("modal-stat-value");
  const modalStatText = document.getElementById("modal-stat-text");
  const modalBodyProse = document.getElementById("modal-body-prose");
  const modalTakeawaysCard = document.getElementById("modal-takeaways-card");
  const modalTakeawaysList = document.getElementById("modal-takeaways-list");

  if (modalCategory) modalCategory.textContent = post.badge || post.category;
  if (modalDate) modalDate.textContent = post.date || "";
  if (modalReadTime) modalReadTime.textContent = post.read_time || "4 min read";

  const isUrdu = post.lang === 'ur' || /[؀-ۿ]/.test(post.title || "");

  if (modalTitle) {
    modalTitle.textContent = post.title;
    modalTitle.className = isUrdu ? "modal-title urdu-title" : "modal-title";
    modalTitle.setAttribute("dir", isUrdu ? "rtl" : "ltr");
  }

  if (modalSubdeck) {
    modalSubdeck.textContent = post.subdeck || "";
    modalSubdeck.className = isUrdu ? "modal-subdeck urdu-subdeck" : "modal-subdeck";
    modalSubdeck.setAttribute("dir", isUrdu ? "rtl" : "ltr");
  }

  if (modalAuthorAvatar) {
    modalAuthorAvatar.src = post.author_avatar || "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop";
    modalAuthorAvatar.alt = post.author || "Kamran Alvi";
  }
  if (modalAuthorName) modalAuthorName.textContent = post.author || "Kamran Alvi";
  if (modalAuthorRole) modalAuthorRole.textContent = post.author_role || "Senior Alpine Expedition Guide";

  if (modalHeroImg) {
    modalHeroImg.src = post.image;
    modalHeroImg.alt = post.title;
  }

  if (modalStatBox) {
    if (post.stat_number) {
      modalStatBox.style.display = "flex";
      if (modalStatValue) modalStatValue.textContent = post.stat_number;
      if (modalStatText) modalStatText.textContent = (post.stat_label || "KEY METRIC") + (post.subdeck ? ": " + post.subdeck : "");
    } else {
      modalStatBox.style.display = "none";
    }
  }

  if (modalBodyProse) {
    modalBodyProse.className = isUrdu ? "modal-article-prose urdu-prose" : "modal-article-prose";
    modalBodyProse.setAttribute("dir", isUrdu ? "rtl" : "ltr");

    if (Array.isArray(post.body)) {
      modalBodyProse.innerHTML = post.body.map(para => `<p>${escapeHtml(para)}</p>`).join("");
    } else if (typeof post.body === "string") {
      modalBodyProse.innerHTML = `<p>${escapeHtml(post.body)}</p>`;
    } else {
      modalBodyProse.innerHTML = `<p>${escapeHtml(post.subdeck || "")}</p>`;
    }
  }

  if (modalTakeawaysCard && modalTakeawaysList) {
    if (post.takeaways && post.takeaways.length > 0) {
      modalTakeawaysCard.style.display = "block";
      modalTakeawaysList.innerHTML = post.takeaways.map(t => `<li ${isUrdu ? 'dir="rtl"' : ''}>${escapeHtml(t)}</li>`).join("");
    } else {
      modalTakeawaysCard.style.display = "none";
    }
  }

  const modalEl = document.getElementById("reader-modal");
  if (modalEl) {
    modalEl.classList.add("open");
    document.body.style.overflow = "hidden";
  }
  window.location.hash = post.id;

  if (window.gtag) {
    window.gtag('event', 'select_content', {
      content_type: 'article',
      item_id: post.id
    });
  }
};

window.closeArticleModal = function() {
  const modalEl = document.getElementById("reader-modal");
  if (modalEl) {
    modalEl.classList.remove("open");
  }
  document.body.style.overflow = "";
  if (window.location.hash) {
    history.replaceState(null, null, window.location.pathname + window.location.search);
  }
};

function initModalListeners() {
  const closeBtn = document.getElementById("modal-close-btn");
  const modalEl = document.getElementById("reader-modal");

  if (closeBtn) {
    closeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      closeArticleModal();
    });
  }

  if (modalEl) {
    modalEl.addEventListener("click", (e) => {
      if (e.target === modalEl) {
        closeArticleModal();
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeArticleModal();
    }
  });

  window.addEventListener("hashchange", () => {
    const hash = window.location.hash.replace("#", "");
    if (hash) {
      openArticleModal(hash);
    } else {
      closeArticleModal();
    }
  });
}

function checkUrlHash() {
  const hash = window.location.hash.replace("#", "");
  if (hash) {
    setTimeout(() => openArticleModal(hash), 150);
  }
}

function initTheme() {
  const saved = localStorage.getItem("dp_theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon(saved);

  const toggleBtn = document.getElementById("theme-toggle-btn");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("dp_theme", next);
      updateThemeIcon(next);
    });
  }
}

function updateThemeIcon(theme) {
  const toggleBtn = document.getElementById("theme-toggle-btn");
  if (!toggleBtn) return;
  toggleBtn.innerHTML = theme === "dark" 
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
}

window.shareStory = function(platform) {
  const url = window.location.href;
  const title = document.getElementById("modal-title") ? document.getElementById("modal-title").textContent : "";
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

function initWebVitalsObservability() {
  if (!('performance' in window) || !('getEntriesByType' in window.performance)) return;
  window.addEventListener('load', () => {
    setTimeout(() => {
      const navEntries = performance.getEntriesByType('navigation');
      if (navEntries.length > 0) {
        const nav = navEntries[0];
        console.log(`[Performance] DOM Complete: ${Math.round(nav.domComplete)}ms | LCP Ready`);
      }
    }, 100);
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
