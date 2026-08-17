/* JD Hub — main.js: theme toggle, navbar behaviour, smooth section reveal */
(function () {
  'use strict';

  // ---- Theme (dark/light) persistence ----
  var root = document.documentElement;
  var stored = localStorage.getItem('jd-theme');
  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  var theme = stored || (prefersDark ? 'dark' : 'light');
  root.setAttribute('data-bs-theme', theme);

  var toggle = document.getElementById('themeToggle');
  if (toggle) {
    syncToggleIcon();
    toggle.addEventListener('click', function () {
      theme = root.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-bs-theme', theme);
      localStorage.setItem('jd-theme', theme);
      syncToggleIcon();
    });
  }
  function syncToggleIcon() {
    if (!toggle) return;
    var isDark = root.getAttribute('data-bs-theme') === 'dark';
    toggle.innerHTML = isDark ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    toggle.classList.toggle('btn-outline-light', !isDark);
    toggle.classList.toggle('btn-outline-warning', isDark);
  }

  // ---- Navbar shrink on scroll ----
  var nav = document.getElementById('mainNav');
  if (nav) {
    var onScroll = function () {
      if (window.scrollY > 30) {
        nav.classList.add('navbar-scrolled');
        nav.style.padding = '.4rem 0';
      } else {
        nav.classList.remove('navbar-scrolled');
        nav.style.padding = '.7rem 0';
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---- Auto-close mobile nav on link click ----
  var navCollapse = document.getElementById('navMain');
  if (navCollapse) {
    navCollapse.querySelectorAll('a.nav-link').forEach(function (link) {
      link.addEventListener('click', function () {
        if (navCollapse.classList.contains('show') && window.bootstrap) {
          window.bootstrap.Collapse.getOrCreateInstance(navCollapse).hide();
        }
      });
    });
  }

  // ---- Reveal on scroll ----
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in-view');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.system-card, .course-card, .service-card, .gallery-item').forEach(function (el) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(18px)';
      el.style.transition = 'opacity .5s ease, transform .5s ease';
      io.observe(el);
    });
    var style = document.createElement('style');
    style.textContent = '.in-view{opacity:1 !important;transform:none !important;}';
    document.head.appendChild(style);
  }

  // ---- Active nav link based on scroll position ----
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('.navbar-jd .nav-link');
  if (sections.length && navLinks.length) {
    window.addEventListener('scroll', function () {
      var pos = window.scrollY + 120;
      sections.forEach(function (sec) {
        if (pos >= sec.offsetTop && pos < sec.offsetTop + sec.offsetHeight) {
          var id = sec.getAttribute('id');
          navLinks.forEach(function (l) {
            l.classList.toggle('active', l.getAttribute('href') && l.getAttribute('href').indexOf('#' + id) > -1);
          });
        }
      });
    }, { passive: true });
  }
})();
