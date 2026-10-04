/**
 * 🛰️ Autonomous Telemetry & Traffic Attribution Engine
 * ====================================================
 * Captures real-time visitor origin, active dwell time per article,
 * scroll completion milestones, cookie audits, and device diagnostics.
 */

(function () {
  'use strict';

  // 1. Traffic Attribution Parser
  function parseTrafficSource() {
    var ref = document.referrer || '';
    var params = new URLSearchParams(window.location.search);
    var utmSource = params.get('utm_source');
    var utmMedium = params.get('utm_medium');
    var utmCampaign = params.get('utm_campaign');
    var utmContent = params.get('utm_content');

    var source = 'Direct / Organic';
    var channel = 'direct';

    if (utmSource) {
      source = utmSource;
      channel = utmMedium || 'campaign';
    } else if (ref) {
      var lowRef = ref.toLowerCase();
      if (lowRef.indexOf('instagram.com') !== -1 || params.has('igshid')) {
        source = 'Instagram';
        channel = 'social';
      } else if (lowRef.indexOf('facebook.com') !== -1 || lowRef.indexOf('fb.me') !== -1 || params.has('fbclid')) {
        source = 'Facebook';
        channel = 'social';
      } else if (lowRef.indexOf('threads.net') !== -1) {
        source = 'Threads';
        channel = 'social';
      } else if (lowRef.indexOf('t.co') !== -1 || lowRef.indexOf('twitter.com') !== -1 || lowRef.indexOf('x.com') !== -1) {
        source = 'X / Twitter';
        channel = 'social';
      } else if (lowRef.indexOf('whatsapp') !== -1 || lowRef.indexOf('wa.me') !== -1) {
        source = 'WhatsApp';
        channel = 'messaging';
      } else if (lowRef.indexOf('google.') !== -1) {
        source = 'Google Search';
        channel = 'organic_search';
      } else if (lowRef.indexOf('bing.com') !== -1) {
        source = 'Bing Search';
        channel = 'organic_search';
      } else if (lowRef.indexOf('youtube.com') !== -1) {
        source = 'YouTube';
        channel = 'social_video';
      } else {
        try {
          source = new URL(ref).hostname;
          channel = 'referral';
        } catch (e) {
          source = 'External Referral';
          channel = 'referral';
        }
      }
    }

    return {
      source: source,
      channel: channel,
      referrer: ref,
      utmSource: utmSource,
      utmMedium: utmMedium,
      utmCampaign: utmCampaign,
      utmContent: utmContent
    };
  }

  // 2. Cookie & Storage Diagnostic
  function getCookieAndStorageTelemetry() {
    var rawCookie = document.cookie || '';
    var cookieList = rawCookie ? rawCookie.split(';').map(function (c) { return c.trim().split('=')[0]; }) : [];
    var localStorageOk = false;
    try {
      localStorage.setItem('__telemetry_test', '1');
      localStorage.removeItem('__telemetry_test');
      localStorageOk = true;
    } catch (e) {}

    return {
      cookiesEnabled: navigator.cookieEnabled,
      cookieCount: cookieList.length,
      cookieNames: cookieList,
      localStorageAvailable: localStorageOk,
      sessionStorageAvailable: typeof sessionStorage !== 'undefined'
    };
  }

  // 3. Device & Network Telemetry
  function getDeviceTelemetry() {
    var ua = navigator.userAgent;
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
    var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

    return {
      deviceType: isMobile ? 'Mobile' : (window.innerWidth < 1024 ? 'Tablet' : 'Desktop'),
      screenWidth: screen.width,
      screenHeight: screen.height,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio || 1,
      language: navigator.language || 'en',
      connectionType: conn ? conn.effectiveType : 'unknown',
      downlinkMbps: conn ? conn.downlink : 'unknown',
      touchPoints: navigator.maxTouchPoints || 0
    };
  }

  // 4. State Management & Dwell Tracking
  var traffic = parseTrafficSource();
  var cookies = getCookieAndStorageTelemetry();
  var device = getDeviceTelemetry();

  var currentArticleId = window.location.hash ? window.location.hash.replace('#', '') : 'feed_overview';
  var isTabActive = document.visibilityState === 'visible';

  // Load persistent stats for local dashboard
  var STORAGE_KEY = 'telemetry_analytics_v1';
  var localData = {
    totalSessions: 0,
    sources: {},
    articleDwellSeconds: {},
    lastUpdated: Date.now()
  };

  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      localData = Object.assign(localData, JSON.parse(stored));
    }
  } catch (e) {}

  localData.totalSessions += 1;
  localData.sources[traffic.source] = (localData.sources[traffic.source] || 0) + 1;

  function persistStats() {
    try {
      localData.lastUpdated = Date.now();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(localData));
    } catch (e) {}
  }
  persistStats();

  // Active Dwell Timer
  document.addEventListener('visibilitychange', function () {
    isTabActive = document.visibilityState === 'visible';
  });

  window.addEventListener('hashchange', function () {
    var newHash = window.location.hash ? window.location.hash.replace('#', '') : 'feed_overview';
    currentArticleId = newHash;
    trackEvent('article_view_switched', { article_id: currentArticleId });
  });

  setInterval(function () {
    if (isTabActive) {
      localData.articleDwellSeconds[currentArticleId] = (localData.articleDwellSeconds[currentArticleId] || 0) + 1;
      var curSeconds = localData.articleDwellSeconds[currentArticleId];

      if ([5, 15, 30, 60, 120, 240].indexOf(curSeconds) !== -1) {
        trackEvent('article_dwell_heartbeat', {
          article_id: currentArticleId,
          dwell_seconds: curSeconds,
          source: traffic.source
        });
      }
      persistStats();
      updateHudUI();
    }
  }, 1000);

  // 5. Scroll Depth Milestones
  var scrollMilestones = { '25': false, '50': false, '75': false, '100': false };
  function checkScroll() {
    var h = document.documentElement;
    var b = document.body;
    var st = 'scrollTop';
    var sh = 'scrollHeight';
    var percent = Math.round(((h[st] || b[st]) / ((h[sh] || b[sh]) - h.clientHeight)) * 100);

    ['25', '50', '75', '100'].forEach(function (m) {
      if (percent >= parseInt(m, 10) && !scrollMilestones[m]) {
        scrollMilestones[m] = true;
        trackEvent('scroll_milestone', { percent: m, article_id: currentArticleId });
      }
    });
  }
  window.addEventListener('scroll', checkScroll, { passive: true });

  // 6. Unified Event Dispatcher
  function trackEvent(name, data) {
    var payload = Object.assign({
      event: name,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      traffic_source: traffic.source,
      traffic_channel: traffic.channel,
      device_type: device.deviceType
    }, data);

    // Forward to GA4 if active
    if (window.gtag) {
      try {
        window.gtag('event', name, payload);
      } catch (e) {}
    }

    // Console logging for developers
    if (window.location.search.indexOf('debug_telemetry=true') !== -1) {
      console.log('📡 [Telemetry]', name, payload);
    }
  }

  // Initial Landing Notification
  trackEvent('session_landing', {
    referrer: traffic.referrer,
    utm_source: traffic.utmSource,
    cookies_enabled: cookies.cookiesEnabled,
    connection_type: device.connectionType
  });

  // 7. Telemetry HUD (Press Ctrl+Alt+T or append #telemetry-hud)
  function createTelemetryHud() {
    var hud = document.createElement('div');
    hud.id = 'telemetry-hud-overlay';
    hud.style.cssText = 'position:fixed;bottom:20px;right:20px;width:380px;max-height:85vh;overflow-y:auto;background:rgba(15,23,42,0.95);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.15);border-radius:16px;color:#f8fafc;font-family:system-ui,-apple-system,sans-serif;font-size:12px;padding:20px;box-shadow:0 20px 40px rgba(0,0,0,0.5);z-index:999999;display:none;';

    hud.innerHTML = [
      '<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:10px;margin-bottom:14px;">',
      '  <span style="font-weight:700;font-size:14px;color:#38bdf8;">🛰️ Real-Time Telemetry HUD</span>',
      '  <button id="close-telemetry-hud" style="background:none;border:none;color:#94a3b8;font-size:16px;cursor:pointer;">✕</button>',
      '</div>',
      '<div id="hud-content"></div>'
    ].join('');

    document.body.appendChild(hud);

    document.getElementById('close-telemetry-hud').onclick = function () {
      hud.style.display = 'none';
    };

    return hud;
  }

  function updateHudUI() {
    var hud = document.getElementById('telemetry-hud-overlay');
    if (!hud || hud.style.display === 'none') return;
    var content = document.getElementById('hud-content');
    if (!content) return;

    var sortedArticles = Object.keys(localData.articleDwellSeconds)
      .map(function (k) { return { id: k, time: localData.articleDwellSeconds[k] }; })
      .sort(function (a, b) { return b.time - a.time; });

    var articlesHtml = sortedArticles.map(function (a) {
      return '<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.05);">' +
        '<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px;color:' + (a.id === currentArticleId ? '#38bdf8;font-weight:700;' : '#e2e8f0;') + '">' + a.id + '</span>' +
        '<span style="color:#f59e0b;font-weight:700;">' + a.time + 's</span>' +
      '</div>';
    }).join('');

    var sourcesHtml = Object.keys(localData.sources).map(function (s) {
      return '<div style="display:flex;justify-content:space-between;padding:2px 0;">' +
        '<span>' + s + '</span>' +
        '<span style="color:#10b981;font-weight:700;">' + localData.sources[s] + '</span>' +
      '</div>';
    }).join('');

    content.innerHTML = [
      '<div style="margin-bottom:12px;">',
      '  <div style="font-weight:700;color:#94a3b8;margin-bottom:4px;text-transform:uppercase;font-size:10px;">Traffic Attribution</div>',
      '  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:8px;">',
      '    <div><b>Active Source:</b> <span style="color:#10b981;">' + traffic.source + ' (' + traffic.channel + ')</span></div>',
      '    <div><b>Referrer:</b> <span style="color:#94a3b8;font-size:11px;">' + (traffic.referrer || 'None (Direct)') + '</span></div>',
      '    <div style="margin-top:4px;">' + sourcesHtml + '</div>',
      '  </div>',
      '</div>',
      '<div style="margin-bottom:12px;">',
      '  <div style="font-weight:700;color:#94a3b8;margin-bottom:4px;text-transform:uppercase;font-size:10px;">Dwell Time per Article (Top Read)</div>',
      '  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:8px;max-height:140px;overflow-y:auto;">',
      '    ' + (articlesHtml || 'No article readings recorded yet.') + '',
      '  </div>',
      '</div>',
      '<div style="margin-bottom:12px;">',
      '  <div style="font-weight:700;color:#94a3b8;margin-bottom:4px;text-transform:uppercase;font-size:10px;">Cookies & Storage Diagnostic</div>',
      '  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:8px;">',
      '    <div><b>Cookies Enabled:</b> ' + (cookies.cookiesEnabled ? '✅ Yes' : '❌ No') + ' (' + cookies.cookieCount + ' active)</div>',
      '    <div><b>Storage Health:</b> ' + (cookies.localStorageAvailable ? '✅ LocalStorage OK' : '⚠️ Storage Restricted') + '</div>',
      '  </div>',
      '</div>',
      '<div>',
      '  <div style="font-weight:700;color:#94a3b8;margin-bottom:4px;text-transform:uppercase;font-size:10px;">Device & Network</div>',
      '  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:8px;">',
      '    <div><b>Device:</b> ' + device.deviceType + ' (' + device.viewportWidth + 'x' + device.viewportHeight + ')</div>',
      '    <div><b>Connection:</b> ' + device.connectionType + ' (~' + device.downlinkMbps + ' Mbps)</div>',
      '  </div>',
      '</div>'
    ].join('');
  }

  // Toggle HUD with shortcut Ctrl+Alt+T or #telemetry-hud
  window.toggleTelemetryHud = function () {
    var hud = document.getElementById('telemetry-hud-overlay') || createTelemetryHud();
    hud.style.display = (hud.style.display === 'none' || !hud.style.display) ? 'block' : 'none';
    updateHudUI();
  };

  window.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.altKey && (e.key === 't' || e.key === 'T')) {
      window.toggleTelemetryHud();
    }
  });

  if (window.location.hash === '#telemetry-hud') {
    setTimeout(function () { window.toggleTelemetryHud(); }, 600);
  }

  // Expose public API
  window.SiteTelemetry = {
    getTrafficSource: parseTrafficSource,
    getCookieData: getCookieAndStorageTelemetry,
    getDeviceData: getDeviceTelemetry,
    getTopArticles: function () {
      return Object.keys(localData.articleDwellSeconds)
        .map(function (k) { return { id: k, seconds: localData.articleDwellSeconds[k] }; })
        .sort(function (a, b) { return b.seconds - a.seconds; });
    },
    showHud: window.toggleTelemetryHud
  };
})();