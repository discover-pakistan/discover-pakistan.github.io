/**
 * Discover Pakistan — High-Performance Editorial Engine
 * Features: Instant 0ms Hydration, Core Web Vitals Telemetry,
 * Scroll Depth Observability & In-Article Ad Monetization.
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

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initWebVitalsObservability();
  initAnchorAdControls();
  initSearch();
  initModalListeners();
  checkUrlHash();

  if (!allPosts || allPosts.length === 0) {
    loadPostsFallback();
  }
});

async function loadPostsFallback() {
  try {
    const res = await fetch("posts.json");
    if (res.ok) {
      allPosts = await res.json();
      renderAll();
    }
  } catch (err) {
    console.warn("Could not fetch posts.json:", err);
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
    featuredSlot.innerHTML = `<div class="p-8 text-center text-muted" style="padding:48px; text-align:center; color:var(--text-muted);">No reports found matching "${escapeHtml(searchQuery)}".</div>`;
    stackSlot.innerHTML = "";
    return;
  }

  const leadPost = filtered[0];
  featuredSlot.innerHTML = `
    <div class="featured-lead-card" onclick="openArticleModal('${leadPost.id}')">
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
      <h2 class="featured-title">${escapeHtml(leadPost.title)}</h2>
      <p class="featured-subdeck">${escapeHtml(leadPost.subdeck)}</p>
      <div class="author-meta-row">
        <img class="author-avatar" src="${leadPost.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(leadPost.author)}" width="24" height="24" loading="lazy" decoding="async" />
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
        <img class="stacked-thumb-img" src="${post.image}" alt="${escapeHtml(post.title)}" width="480" height="270" loading="lazy" decoding="async" />
      </div>
      <div class="stacked-story-info">
        <h3 class="stacked-story-title">${escapeHtml(post.title)}</h3>
        <p class="stacked-story-excerpt">${escapeHtml(post.subdeck)}</p>
        <div class="author-meta-row">
          <img class="author-avatar" src="${post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(post.author)}" width="24" height="24" loading="lazy" decoding="async" />
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
        <p style="font-size: 1.1rem; margin-bottom: 8px;">No additional dossiers in this category.</p>
        <button class="pill-btn active" onclick="setCategory('All')">View All Reports</button>
      </div>
    `;
    return;
  }

  editorialGrid.innerHTML = gridPosts.map(post => `
    <div class="editorial-card" onclick="openArticleModal('${post.id}')">
      <div class="editorial-card-thumb">
        <img class="editorial-card-img" src="${post.image}" alt="${escapeHtml(post.title)}" width="600" height="338" loading="lazy" decoding="async" />
        ${post.badge ? `<span class="media-badge">${escapeHtml(post.badge)}</span>` : ''}
      </div>
      <div class="card-category-tag">${escapeHtml(post.category)}</div>
      <h3 class="editorial-card-title">${escapeHtml(post.title)}</h3>
      <p class="editorial-card-excerpt">${escapeHtml(post.subdeck)}</p>
      <div class="author-meta-row">
        <img class="author-avatar" src="${post.author_avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop'}" alt="${escapeHtml(post.author)}" width="24" height="24" loading="lazy" decoding="async" />
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

  articleStartTime = Date.now();

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

  const isUrdu = post.lang === 'ur' || /[؀-ۿ]/.test(post.title);
  if (isUrdu) {
    modalTitle.style.direction = "rtl";
    modalTitle.style.textAlign = "right";
    modalTitle.style.fontFamily = "'Noto Nastaliq Urdu', 'Amiri', serif";
    modalTitle.style.lineHeight = "1.8";

    modalSubdeck.style.direction = "rtl";
    modalSubdeck.style.textAlign = "right";
    modalSubdeck.style.fontFamily = "'Noto Nastaliq Urdu', 'Amiri', serif";
    modalSubdeck.style.lineHeight = "1.9";

    modalBodyProse.style.direction = "rtl";
    modalBodyProse.style.textAlign = "right";
    modalBodyProse.style.fontFamily = "'Noto Nastaliq Urdu', 'Amiri', serif";
    modalBodyProse.style.lineHeight = "2.3";
    modalBodyProse.style.fontSize = "1.1rem";

    modalTakeawaysList.style.direction = "rtl";
    modalTakeawaysList.style.textAlign = "right";
    modalTakeawaysList.style.fontFamily = "'Noto Nastaliq Urdu', 'Amiri', serif";
    modalTakeawaysList.style.lineHeight = "2.0";
  } else {
    modalTitle.style.direction = "ltr";
    modalTitle.style.textAlign = "left";
    modalTitle.style.fontFamily = "";
    modalTitle.style.lineHeight = "";

    modalSubdeck.style.direction = "ltr";
    modalSubdeck.style.textAlign = "left";
    modalSubdeck.style.fontFamily = "";
    modalSubdeck.style.lineHeight = "";

    modalBodyProse.style.direction = "ltr";
    modalBodyProse.style.textAlign = "left";
    modalBodyProse.style.fontFamily = "";
    modalBodyProse.style.lineHeight = "";
    modalBodyProse.style.fontSize = "";

    modalTakeawaysList.style.direction = "ltr";
    modalTakeawaysList.style.textAlign = "left";
    modalTakeawaysList.style.fontFamily = "";
    modalTakeawaysList.style.lineHeight = "";
  }

  if (post.stat_number) {
    modalStatBox.style.display = "flex";
    modalStatValue.textContent = post.stat_number;
    modalStatText.textContent = (post.stat_label || "KEY METRIC") + ": " + (post.subdeck || "");
  } else {
    modalStatBox.style.display = "none";
  }

  // High-dwell in-article AdSense unit inserted after paragraph 2
  const inArticleAdHtml = `
    <div class="ad-slot-wrapper ad-in-article" style="margin: 28px 0; border: 1px dashed var(--border-color); border-radius: 8px; padding: 12px; background: rgba(0,0,0,0.02); text-align: center;">
      <span class="ad-label" style="display:block; font-size: 0.65rem; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px; font-weight: 700; text-transform: uppercase;">Sponsored Recommendation</span>
      <ins class="adsbygoogle"
           style="display:block; text-align:center; min-height: 250px;"
           data-ad-layout="in-article"
           data-ad-format="fluid"
           data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
           data-ad-slot="1122334455"></ins>
    </div>
  `;

  if (Array.isArray(post.body)) {
    if (post.body.length > 2) {
      const p1_2 = post.body.slice(0, 2).map(p => `<p>${escapeHtml(p)}</p>`).join("");
      const pRem = post.body.slice(2).map(p => `<p>${escapeHtml(p)}</p>`).join("");
      modalBodyProse.innerHTML = p1_2 + inArticleAdHtml + pRem;
    } else {
      modalBodyProse.innerHTML = post.body.map(para => `<p>${escapeHtml(para)}</p>`).join("") + inArticleAdHtml;
    }
  } else if (typeof post.body === "string") {
    modalBodyProse.innerHTML = `<p>${escapeHtml(post.body)}</p>` + inArticleAdHtml;
  } else {
    modalBodyProse.innerHTML = `<p>${escapeHtml(post.subdeck)}</p>` + inArticleAdHtml;
  }

  try {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  } catch (e) {}

  if (post.takeaways && post.takeaways.length > 0) {
    modalTakeawaysCard.style.display = "block";
    modalTakeawaysList.innerHTML = post.takeaways.map(t => `<li>${escapeHtml(t)}</li>`).join("");
  } else {
    modalTakeawaysCard.style.display = "none";
  }

  readerModal.classList.add("open");
  document.body.style.overflow = "hidden";
  window.location.hash = post.id;

  trackArticleScroll(post.id);

  if (window.gtag) {
    window.gtag('event', 'select_content', {
      content_type: 'article',
      item_id: post.id
    });
  }
};

window.closeArticleModal = function() {
  if (articleStartTime && window.gtag) {
    const dwellSeconds = Math.round((Date.now() - articleStartTime) / 1000);
    window.gtag('event', 'user_engagement', {
      engagement_time_msec: dwellSeconds * 1000
    });
  }

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
    setTimeout(() => openArticleModal(hash), 100);
  }
}

function initAnchorAdControls() {
  const anchorClose = document.getElementById("anchor-close-btn");
  if (anchorClose) {
    anchorClose.addEventListener("click", () => {
      const anchor = document.getElementById("sticky-anchor-ad");
      if (anchor) anchor.style.display = "none";
    });
  }
}

function trackArticleScroll(postId) {
  const readerBody = document.querySelector(".reader-modal-body");
  if (!readerBody) return;

  const thresholds = [25, 50, 75, 100];
  const reached = new Set();

  const handleScroll = () => {
    const total = readerBody.scrollHeight - readerBody.clientHeight;
    if (total <= 0) return;
    const progress = Math.min(100, Math.round((readerBody.scrollTop / total) * 100));

    thresholds.forEach(pct => {
      if (progress >= pct && !reached.has(pct)) {
        reached.add(pct);
        if (window.gtag) {
          window.gtag('event', 'scroll_depth', {
            post_id: postId,
            depth_percent: pct
          });
        }
      }
    });
  };

  readerBody.removeEventListener("scroll", handleScroll);
  readerBody.addEventListener("scroll", handleScroll, { passive: true });
}

function initWebVitalsObservability() {
  if (!('PerformanceObserver' in window)) return;

  function reportMetric(name, value, rating) {
    if (window.gtag) {
      window.gtag('event', 'web_vitals', {
        metric_name: name,
        metric_value: Math.round(value),
        metric_rating: rating,
        non_interaction: true
      });
    }
  }

  try {
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lastEntry = entries[entries.length - 1];
      if (lastEntry) {
        const lcp = lastEntry.renderTime || lastEntry.loadTime;
        const rating = lcp < 2500 ? 'good' : (lcp < 4000 ? 'needs-improvement' : 'poor');
        reportMetric('LCP', lcp, rating);
      }
    }).observe({ type: 'largest-contentful-paint', buffered: true });

    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        const fid = entry.processingStart - entry.startTime;
        const rating = fid < 100 ? 'good' : (fid < 300 ? 'needs-improvement' : 'poor');
        reportMetric('FID', fid, rating);
      }
    }).observe({ type: 'first-input', buffered: true });

    let clsValue = 0;
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
          const rating = clsValue < 0.1 ? 'good' : (clsValue < 0.25 ? 'needs-improvement' : 'poor');
          reportMetric('CLS', clsValue * 1000, rating);
        }
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (e) {}
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
