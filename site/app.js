/* Physics 2027 Question Lab — dependency-light GitHub Pages frontend */
(() => {
  'use strict';

  const SITE_NAME = 'Physics 2027 · Question Lab';
  const STORE_KEY = 'physics2027-question-progress-v1';
  const THEME_KEY = 'physics2027-theme';
  const ROUTES = ['overview', 'practice', 'archive', 'roadmap', 'resources'];
  const LABELS = {
    overview: 'Overview', practice: 'Daily practice', archive: 'Question archive',
    roadmap: 'Study roadmap', resources: 'Resources'
  };
  const EXAMS = [
    { code: 'TIFR GS', date: '2026-12-13', label: '13 DEC 2026', time: '2:00–5:00 PM', category: 'CONCEPTUAL REASONING' },
    { code: 'CSIR-UGC NET', date: '2026-12-27', label: '27 DEC 2026', time: '3:00–6:00 PM', category: 'ANALYTICAL / PART C' },
    { code: 'GATE PH', date: null, label: 'FEBRUARY 2027', time: 'PH slot: verify officially', category: 'NUMERICAL PRECISION' },
    { code: 'JAM PH', date: '2027-02-14', label: '14 FEB 2027', time: '2:30–5:30 PM', category: 'MCQ / MSQ / NAT' }
  ];
  const $ = (selector) => document.querySelector(selector);
  const content = $('#content');
  const state = {
    database: null, view: 'overview', date: null, subject: 'All subjects',
    search: '', progress: readJSON(STORE_KEY, {}), docs: {},
    theme: localStorageGet(THEME_KEY) || 'dark'
  };
  let toastTimeout = null;

  function localStorageGet(key) {
    try { return localStorage.getItem(key); } catch (_) { return null; }
  }
  function readJSON(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch (_) { return fallback; }
  }
  function writeJSON(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* No persistence in strict private mode. */ }
  }
  function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]
    ));
  }
  function parseMarkdown(value) {
    const tokens = [];
    const protectedText = String(value || '').replace(/\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$\$[\s\S]*?\$\$/g, match => {
      const token = 'PHYSXMATHTOKEN' + tokens.length + 'END';
      tokens.push(match);
      return token;
    });
    let html;
    if (window.marked && typeof window.marked.parse === 'function') {
      html = window.marked.parse(protectedText, { gfm: true, breaks: false });
      if (window.DOMPurify) {
        html = window.DOMPurify.sanitize(html);
      }
    } else {
      html = '<p>' + esc(protectedText).replace(/\n{2,}/g, '</p><p>').replace(/\n/g, '<br>') + '</p>';
    }
    return String(html).replace(/PHYSXMATHTOKEN(\d+)END/g, (_, index) =>
      '<span class="math-render">' + esc(tokens[Number(index)]) + '</span>');
  }
  function typeset() {
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
      window.MathJax.typesetPromise([content]).catch(() => {});
    }
  }
  function niceDate(iso, options = { day: 'numeric', month: 'long', year: 'numeric' }) {
    return new Intl.DateTimeFormat('en-IN', { ...options, timeZone: 'UTC' }).format(new Date(iso + 'T12:00:00Z'));
  }
  function todayIST() {
    return new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Kolkata', year: 'numeric', month: '2-digit', day: '2-digit'
    }).format(new Date());
  }
  function latest() {
    return state.database && state.database.days[0];
  }
  function chosenDay() {
    return (state.database?.days || []).find(d => d.date === state.date) || latest();
  }
  function allQuestions() {
    return (state.database?.days || []).flatMap(d => d.questions);
  }
  function completedIds() {
    return Object.keys(state.progress).filter(k => state.progress[k]);
  }
  function totalCompleted() {
    return allQuestions().filter(q => !!state.progress[q.id]).length;
  }
  function progressFor(day) {
    return day ? day.questions.filter(q => !!state.progress[q.id]).length : 0;
  }
  function slugHash(route, date) {
    return '#' + route + (route === 'practice' && date ? '/' + date : '');
  }
  function go(route, date) {
    const nextHash = slugHash(route, date);
    if (window.location.hash === nextHash) onRoute();
    else window.location.hash = nextHash;
  }
  function screenName() {
    const slug = (window.location.hash || '#overview').slice(1).split('/');
    state.view = ROUTES.includes(slug[0]) ? slug[0] : 'overview';
    const valid = /^\d{4}-\d{2}-\d{2}$/.test(slug[1] || '') ? slug[1] : null;
    if (valid && state.database?.days.some(d => d.date === valid)) state.date = valid;
    if (!state.date || !state.database?.days.some(d => d.date === state.date)) state.date = latest()?.date || null;
  }
  function closeMenu() {
    $('#sidebar').classList.remove('open');
    $('#mobileShade').hidden = true;
    $('#menuToggle').setAttribute('aria-expanded', 'false');
  }
  function renderShell() {
    $('#routeLabel').textContent = LABELS[state.view] || 'Overview';
    $('#headerDate').textContent = new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Asia/Kolkata', day: '2-digit', month: 'short', year: 'numeric'
    }).format(new Date()).toUpperCase();
    document.querySelectorAll('[data-route]').forEach(button => {
      const active = button.dataset.route === state.view;
      button.classList.toggle('active', active);
      if (active) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    closeMenu();
  }
  function statCard(label, value, note, color='') {
    return '<div class="stat-card"><div class="stat-label">' + esc(label) +
      '</div><div class="stat-value ' + color + '">' + esc(value) +
      '</div><div class="stat-foot">' + esc(note) + '</div></div>';
  }
  function dayProgressBar(day) {
    const count = progressFor(day);
    const pct = day ? Math.round(count / day.questions.length * 100) : 0;
    return '<div class="progress-track"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
      '<div class="progress-caption"><span>' + count + '/' + (day?.questions.length || 0) +
      ' questions completed on this device</span><span>' + pct + '%</span></div>';
  }
  function examCards() {
    return EXAMS.map(e =>
      '<div class="exam-card"><div class="mini-tag">' + esc(e.label) +
      '</div><h3>' + esc(e.code) + '</h3><p>' + esc(e.category) +
      '</p><p style="margin-top:10px">' + esc(e.time) + '</p></div>'
    ).join('');
  }
  function dashboard() {
    const day = latest();
    if (!day) return '<div class="empty-state">No questions have been published.</div>';
    const days = state.database.days.length;
    const all = state.database.totalQuestions;
    const count = totalCompleted();
    const latestCompleted = progressFor(day);
    return '<div class="hero">' +
      '<div class="eyebrow">A CONCEPT-FIRST PHYSICS STUDY SPACE</div>' +
      '<h1>Think deeper.<br><em>Solve smarter.</em></h1>' +
      '<p>One workspace for TIFR GS, CSIR-UGC NET, GATE PH and IIT JAM PH 2027. Build your fundamentals, take on ten solved problems, and track what you truly understand.</p>' +
      '<div class="button-row"><button class="button button-primary" data-action="latest">START TODAY’S PRACTICE <span>↗</span></button>' +
      '<button class="button" data-route-target="roadmap">EXPLORE STUDY PLAN <span>↗</span></button></div></div>' +
      '<div class="stats-grid">' +
      statCard('PUBLISHED SETS', days, 'Dated daily problem sheets') +
      statCard('TOTAL QUESTIONS', all, 'With worked solutions', 'blue') +
      statCard('YOUR SOLVED TOTAL', count, 'Stored in this browser', 'green') +
      statCard('LATEST SET DONE', latestCompleted + '/10', 'Published ' + niceDate(day.date, { day:'numeric', month:'short' }), 'gold') +
      '</div>' +
      '<div class="section-head"><div><h2>Continue your practice</h2><p>Your latest published set, ready to solve.</p></div>' +
      '<button class="text-action" data-route-target="archive">EXPLORE ARCHIVE ↗</button></div>' +
      '<div class="split-layout"><div class="feature-panel"><div class="feature-top">' +
      '<span class="pill">● LATEST PUBLISHED SET</span><span class="small-muted">' + esc(niceDate(day.date)) + '</span></div>' +
      '<h3>10 questions. 10 concepts.<br>One stronger foundation.</h3>' +
      '<p>Mathematics, mechanics, electrodynamics, quantum theory, thermal physics, optics, and more. Attempt each problem before opening the solution.</p>' +
      '<button class="button button-primary" data-action="latest">OPEN QUESTION SET ↗</button>' +
      dayProgressBar(day) + '</div>' +
      '<div class="side-panel"><h3>YOUR EXAM PREPARATION PATH</h3><div class="timeline">' +
      '<div class="timeline-row"><div class="timeline-node"></div><div><h4>01 · Foundation / diagnostic</h4><p>Math, mechanics, E&M and quantum essentials.</p></div></div>' +
      '<div class="timeline-row"><div class="timeline-node"></div><div><h4>02 · December: TIFR + NET</h4><p>Conceptual reasoning then Part C analytical practice.</p></div></div>' +
      '<div class="timeline-row"><div class="timeline-node"></div><div><h4>03 · January: GATE + JAM</h4><p>Finish remaining syllabus, tackle PYQs and mocks.</p></div></div>' +
      '<div class="timeline-row"><div class="timeline-node"></div><div><h4>04 · February: exam phase</h4><p>Timed papers, accuracy, and strategic revision.</p></div></div>' +
      '</div></div></div>' +
      '<div class="section-head"><div><h2>2027 examination milestones</h2><p>Confirm final instructions on official exam websites.</p></div></div>' +
      '<div class="exam-grid">' + examCards() + '</div>' +
      '<div class="callout"><span style="font-size:21px">✧</span><div><strong>Understand → derive → solve → review.</strong>' +
      '<p>Fresh practice sets are scheduled for 08:00 IST each day (GitHub Actions scheduling may be delayed). These are original, rotating exercises—not copied previous-year papers.</p></div></div>';
  }

  function practice() {
    const day = chosenDay();
    if (!day) return '<div class="empty-state">No dated question files found.</div>';
    const subjects = ['All subjects', ...new Set(day.questions.map(q => q.subject))].sort((a,b)=>
      a === 'All subjects' ? -1 : b === 'All subjects' ? 1 : a.localeCompare(b));
    if (!subjects.includes(state.subject)) state.subject = 'All subjects';
    return '<div class="page-header"><div class="eyebrow">DAILY PROBLEM SOLVING</div>' +
      '<h1 class="page-title">Practice with purpose.</h1><p class="page-intro">Each dated set has ten original questions with worked solutions. Try the problem, show the solution, then mark it complete. Progress stays on this device.</p></div>' +
      '<div class="daily-header"><div class="daily-meta"><span class="pill">TEN-QUESTION SESSION</span>' +
      '<span class="small-muted">Published: ' + esc(niceDate(day.date)) + '</span></div>' +
      '<select class="date-select" id="dateSelect" aria-label="Select question date">' +
      state.database.days.map(d => '<option value="' + esc(d.date) + '"' +
      (d.date === day.date ? ' selected' : '') + '>' + esc(niceDate(d.date)) +
      (d.date === latest().date ? ' · Latest' : '') + '</option>').join('') + '</select></div>' +
      '<div class="feature-panel" style="margin-bottom:20px"><div class="feature-top"><strong>Session progress</strong>' +
      '<span class="small-muted">No timer required · Focus on understanding</span></div>' +
      dayProgressBar(day) + '</div>' +
      '<div class="toolbar"><label class="search-field"><span>⌕</span><input id="questionSearch" placeholder="Search topics or question text" autocomplete="off" value="' + esc(state.search) + '"></label>' +
      '<select id="subjectFilter" aria-label="Filter by subject">' +
      subjects.map(s => '<option value="' + esc(s) + '"' +
        (s === state.subject ? ' selected' : '') + '>' + esc(s) + '</option>').join('') +
      '</select></div><div class="small-muted" id="questionCount"></div><div class="question-stack" id="questionList" style="margin-top:14px"></div>' +
      '<div class="callout"><span style="font-size:20px">↗</span><div><strong>Need real previous-year problems?</strong><p>Use the <a href="#resources" style="text-decoration:underline">official PYQ resources</a>. Daily practice here is original, and selected topic families repeat with changing parameters.</p></div></div>';
  }

  function questionsHTML(day, items) {
    if (!items.length) return '<div class="empty-state"><strong>No questions match.</strong>Try clearing the search or selecting another subject.</div>';
    return items.map(q => {
      const done = !!state.progress[q.id];
      return '<article class="question-card" data-question-card="' + esc(q.id) + '">' +
        '<div class="question-header"><div><div class="q-index">QUESTION ' + String(q.number).padStart(2,'0') + ' / 10</div>' +
        '<h2 class="q-heading">' + esc(q.topic) + '</h2><div class="q-meta">' + esc(q.subject) + ' · ' + esc(day.dayLabel) + '</div></div>' +
        '<button class="q-done' + (done ? ' is-done' : '') + '" data-done="' + esc(q.id) +
        '" aria-pressed="' + done + '">' + (done ? '✓ COMPLETED' : '○ MARK COMPLETE') + '</button></div>' +
        '<div class="q-content">' + parseMarkdown(q.question) + '</div>' +
        '<details class="solution"><summary>VIEW STEP-BY-STEP SOLUTION</summary><div class="solution-body">' + parseMarkdown(q.solution) +
        '</div></details></article>';
    }).join('');
  }
  function updateQuestions() {
    const day = chosenDay();
    const list = $('#questionList');
    if (!day || !list) return;
    const search = state.search.trim().toLowerCase();
    const filtered = day.questions.filter(q =>
      (state.subject === 'All subjects' || state.subject === q.subject) &&
      (!search || (q.subject + ' ' + q.topic + ' ' + q.question).toLowerCase().includes(search)));
    list.innerHTML = questionsHTML(day, filtered);
    const count = $('#questionCount');
    if (count) count.textContent = 'SHOWING ' + filtered.length + ' OF ' + day.questions.length + ' QUESTIONS';
    typeset();
  }

  function archive() {
    const sets = state.database.days;
    return '<div class="page-header"><div class="eyebrow">THE COMPLETE QUESTION LIBRARY</div>' +
      '<h1 class="page-title">Every day, documented.</h1>' +
      '<p class="page-intro">All ten-question sets are organized by publication date. Open any date to continue a practice session. New dates appear here after the scheduled generator publishes them.</p></div>' +
      '<div class="stats-grid" style="margin-bottom:27px">' +
      statCard('ARCHIVED DAYS', sets.length, 'Automatically indexed') +
      statCard('TOTAL QUESTIONS', state.database.totalQuestions, 'With worked explanations', 'blue') +
      statCard('QUESTIONS COMPLETED', totalCompleted(), 'This browser only', 'green') +
      statCard('PUBLISHING', '08:00', 'IST · schedule can be delayed', 'gold') +
      '</div><div class="archive-grid">' +
      sets.map(d => '<button class="archive-card" data-day="' + esc(d.date) + '">' +
        '<span class="archive-day">DAILY SET / ' + esc(d.date) + '</span><h3>' + esc(niceDate(d.date)) + '</h3>' +
        '<p>10 original physics practice questions · complete worked solutions · multiple subject areas.</p>' +
        '<div class="progress-track"><div class="progress-fill" style="width:' + Math.round(progressFor(d)/10*100) + '%"></div></div>' +
        '<div class="archive-bottom"><span>' + progressFor(d) + '/10 completed</span><strong>OPEN SET ↗</strong></div></button>').join('') +
      '</div>';
  }

  async function documentView(which) {
    const id = which === 'roadmap' ? 'roadmap' : 'resources';
    const filename = id === 'roadmap' ? 'roadmap.md' : 'resources.md';
    const heading = id === 'roadmap' ? 'Your route to 2027.' : 'Learn from the right sources.';
    const intro = id === 'roadmap'
      ? 'Build from first principles, then train with past papers and realistic exam timing.'
      : 'Official exam portals, original previous-year question archives, recommended textbooks and free courseware.';
    if (!state.docs[id]) {
      const r = await fetch('./data/' + filename, { cache:'no-store' });
      if (!r.ok) throw new Error('Cannot load study notes (' + r.status + ')');
      state.docs[id] = await r.text();
    }
    // Correct local links from source Markdown to site routes or GitHub source paths.
    const markdown = state.docs[id].replace(/\]\(RESOURCES\.md\)/g, '](#resources)')
      .replace(/\]\(2027-ROADMAP\.md\)/g, '](#roadmap)')
      .replace(/\]\(TRACKER\.md\)/g, '](https://github.com/KrAzad0/QUESTIONS/blob/main/docs/TRACKER.md)')
      .replace(/\]\(\.\.\/questions\/\)/g, '](#archive)');
    return '<div class="page-header"><div class="eyebrow">' + (id === 'roadmap' ? 'THE CONCEPTUAL GAME PLAN' : 'YOUR LEARNING LIBRARY') +
      '</div><h1 class="page-title">' + heading + '</h1><p class="page-intro">' + intro + '</p></div>' +
      '<div class="button-row"><button class="button button-primary" data-action="latest">OPEN DAILY QUESTIONS ↗</button>' +
      '<a class="button" target="_blank" rel="noopener noreferrer" href="https://github.com/KrAzad0/QUESTIONS/blob/main/docs/' +
      (id === 'roadmap' ? '2027-ROADMAP.md' : 'RESOURCES.md') + '">VIEW SOURCE ↗</a></div>' +
      '<div class="doc-card"><div class="doc-content">' + parseMarkdown(markdown) + '</div></div>';
  }

  async function render() {
    if (!state.database) return;
    screenName();
    renderShell();
    if (state.view === 'overview') content.innerHTML = dashboard();
    else if (state.view === 'practice') {
      content.innerHTML = practice();
      updateQuestions();
    }
    else if (state.view === 'archive') content.innerHTML = archive();
    else {
      content.innerHTML = '<div class="loading-card"><span class="loader"></span>Loading notes…</div>';
      try { content.innerHTML = await documentView(state.view); }
      catch (e) { content.innerHTML = '<div class="empty-state"><strong>Could not open this section.</strong>' +
        esc(e.message) + ' · <a href="https://github.com/KrAzad0/QUESTIONS">View on GitHub</a></div>'; }
    }
    document.title = LABELS[state.view] + ' · ' + SITE_NAME;
    typeset();
  }

  function onRoute() {
    render().catch(showError);
    if (window.scrollY > 150) window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  function showError(error) {
    console.error(error);
    content.innerHTML = '<div class="empty-state"><strong>Unable to load the study site.</strong>' +
      '<p>Refresh the page or read the original files on ' +
      '<a href="https://github.com/KrAzad0/QUESTIONS">GitHub</a>.</p></div>';
  }
  function toast(message) {
    const node = $('#toast');
    node.textContent = message;
    node.hidden = false;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => { node.hidden = true; }, 2400);
  }

  document.addEventListener('click', e => {
    const link = e.target.closest('[data-route]');
    if (link) { go(link.dataset.route); return; }
    const quick = e.target.closest('[data-route-target]');
    if (quick) { go(quick.dataset.routeTarget); return; }
    const newSession = e.target.closest('[data-action="latest"]');
    if (newSession) { state.date = latest()?.date; go('practice', state.date); return; }
    const day = e.target.closest('[data-day]');
    if (day) { state.date = day.dataset.day; go('practice', state.date); return; }
    const toggle = e.target.closest('[data-done]');
    if (toggle) {
      const id = toggle.dataset.done;
      state.progress[id] = !state.progress[id];
      if (!state.progress[id]) delete state.progress[id];
      writeJSON(STORE_KEY, state.progress);
      const done = !!state.progress[id];
      toggle.classList.toggle('is-done', done);
      toggle.setAttribute('aria-pressed', String(done));
      toggle.textContent = done ? '✓ COMPLETED' : '○ MARK COMPLETE';
      const day = chosenDay();
      const session = $('.feature-panel .progress-track');
      if (day && session) {
        const n = progressFor(day);
        session.querySelector('.progress-fill').style.width = Math.round(n/10*100) + '%';
        const caption = $('.feature-panel .progress-caption');
        if (caption) caption.innerHTML = '<span>' + n + '/10 questions completed on this device</span><span>' + n*10 + '%</span>';
      }
      toast(done ? 'Question marked completed' : 'Question marked not completed');
    }
  });
  document.addEventListener('input', e => {
    if (e.target?.id === 'questionSearch') {
      state.search = e.target.value;
      updateQuestions();
    }
  });
  document.addEventListener('change', e => {
    if (e.target?.id === 'subjectFilter') {
      state.subject = e.target.value;
      updateQuestions();
    }
    if (e.target?.id === 'dateSelect') {
      state.date = e.target.value;
      state.subject = 'All subjects';
      state.search = '';
      go('practice', state.date);
    }
  });
  $('#themeToggle').addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = state.theme;
    try { localStorage.setItem(THEME_KEY, state.theme); } catch (_) {}
    $('#themeToggle').textContent = state.theme === 'dark' ? '☼' : '☾';
  });
  $('#menuToggle').addEventListener('click', () => {
    const isOpen = $('#sidebar').classList.toggle('open');
    $('#mobileShade').hidden = !isOpen;
    $('#menuToggle').setAttribute('aria-expanded', String(isOpen));
  });
  $('#mobileShade').addEventListener('click', closeMenu);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeMenu();
  });
  window.addEventListener('hashchange', onRoute);

  (async () => {
    document.documentElement.dataset.theme = state.theme;
    $('#themeToggle').textContent = state.theme === 'dark' ? '☼' : '☾';
    $('#headerDate').textContent = new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Asia/Kolkata', day:'2-digit', month:'short', year:'numeric'
    }).format(new Date());
    try {
      const response = await fetch('./data/questions.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Question index HTTP ' + response.status);
      state.database = await response.json();
      if (!Array.isArray(state.database.days) || !state.database.days.length) throw new Error('Empty archive');
      state.database.days.sort((a,b) => b.date.localeCompare(a.date));
      await render();
    } catch (e) { showError(e); }
  })();
})();
