const currencyBRL = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});
const numberFmt = new Intl.NumberFormat("pt-BR");

let allCases = [];
let agcMode = "timeline";
let selectedCaseId = null;
let calendarViewDate = new Date();
let calendarSelectedDate = null;

const layout = document.querySelector(".layout");
const toggleSidebarBtn = document.getElementById("toggle-sidebar");

const kpiGrid = document.getElementById("kpi-grid");
const casesBody = document.getElementById("cases-body");
const resultCount = document.getElementById("result-count");
const refDate = document.getElementById("ref-date");

const phasesBoard = document.getElementById("phases-board");
const agcTimeline = document.getElementById("agc-timeline");
const agcCalendar = document.getElementById("agc-calendar");
const agcNextCount = document.getElementById("agc-next-count");
const agcMissingCount = document.getElementById("agc-missing-count");

const modal = document.getElementById("case-modal");
const closeModalBtn = document.getElementById("close-modal");
const modalTitle = document.getElementById("modal-title");
const modalSubtitle = document.getElementById("modal-subtitle");
const modalKpis = document.getElementById("modal-kpis");
const modalGrid = document.getElementById("modal-grid");
const modalDocs = document.getElementById("modal-docs");

const docsModal = document.getElementById("docs-modal");
const closeDocsModalBtn = document.getElementById("close-docs-modal");
const docsModalTitle = document.getElementById("docs-modal-title");
const docsList = document.getElementById("docs-list");
const editModal = document.getElementById("edit-modal");
const closeEditModalBtn = document.getElementById("close-edit-modal");
const editModalTitle = document.getElementById("edit-modal-title");
const editForm = document.getElementById("edit-form");
const uploadModal = document.getElementById("upload-modal");
const closeUploadModalBtn = document.getElementById("close-upload-modal");
const uploadModalTitle = document.getElementById("upload-modal-title");
const uploadForm = document.getElementById("upload-form");

const filterMissingDocs = document.getElementById("filter-missing-docs");
const filterMissingAgc = document.getElementById("filter-missing-agc");
const filterDelayedAm = document.getElementById("filter-delayed-am");
const filterPm = document.getElementById("filter-pm");
const filterCarteira = document.getElementById("filter-carteira");
const filterRjPhase = document.getElementById("filter-rj-phase");
const filterClass = document.getElementById("filter-class");
const filterStatus = document.getElementById("filter-status");
const filterInvestigacao = document.getElementById("filter-investigacao");
const filterDocsOk = document.getElementById("filter-docs-ok");
const filterAgcOk = document.getElementById("filter-agc-ok");
const filterAgcWindow = document.getElementById("filter-agc-window");
const filterTicket = document.getElementById("filter-ticket");
const filterSearch = document.getElementById("filter-search");
const clearFiltersBtn = document.getElementById("clear-filters");
const activeFiltersEl = document.getElementById("active-filters");
const openAgcCalendarModalBtn = document.getElementById("open-agc-calendar-modal");
const agcCalendarModal = document.getElementById("agc-calendar-modal");
const closeAgcCalendarModalBtn = document.getElementById("close-agc-calendar-modal");
const agcCalPrevBtn = document.getElementById("agc-cal-prev");
const agcCalNextBtn = document.getElementById("agc-cal-next");
const agcCalTitle = document.getElementById("agc-cal-title");
const agcCalGrid = document.getElementById("agc-cal-grid");
const agcCalDayList = document.getElementById("agc-cal-day-list");

function fmtDate(dateStr) {
  if (!dateStr) return "Sem data";
  return new Date(dateStr).toLocaleDateString("pt-BR");
}

function buildKpis(kpis) {
  const cards = [
    { label: "Total de Casos", value: numberFmt.format(kpis.total_cases) },
    { label: "Com Documento Faltando", value: numberFmt.format(kpis.missing_docs_cases) },
    { label: "Sem Data AGC", value: numberFmt.format(kpis.missing_agc_cases) },
    { label: "AM Atrasado", value: numberFmt.format(kpis.delayed_am_cases) },
    { label: "Valor Credito Total", value: currencyBRL.format(kpis.total_credito) },
  ];

  kpiGrid.innerHTML = cards
    .map((card) => `<article class="kpi-card"><div class="label">${card.label}</div><div class="value">${card.value}</div></article>`)
    .join("");
}

function uniqueSorted(list) {
  return [...new Set(list)].sort((a, b) => a.localeCompare(b));
}

function populateSelect(el, values) {
  values.forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    el.appendChild(opt);
  });
}

function setupFilterOptions() {
  populateSelect(filterPm, uniqueSorted(allCases.map((c) => c.pm)));
  populateSelect(filterCarteira, uniqueSorted(allCases.map((c) => c.carteira)));
  populateSelect(filterRjPhase, uniqueSorted(allCases.map((c) => c.rj_phase)));
  populateSelect(filterClass, uniqueSorted(allCases.map((c) => c.class)));
  populateSelect(filterStatus, uniqueSorted(allCases.map((c) => c.status_tag)));
}

function matchTicket(c, band) {
  if (!band) return true;
  if (band === "low") return c.valor_credito <= 70_000_000;
  if (band === "mid") return c.valor_credito > 70_000_000 && c.valor_credito <= 150_000_000;
  return c.valor_credito > 150_000_000;
}

function filteredCases() {
  const search = filterSearch.value.trim().toLowerCase();
  const now = new Date();
  const plus30 = new Date();
  plus30.setDate(plus30.getDate() + 30);
  const nextMonthStart = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const nextMonthEnd = new Date(now.getFullYear(), now.getMonth() + 2, 0);
  return allCases.filter((c) => {
    if (filterMissingDocs.checked && !c.has_missing_docs) return false;
    if (filterMissingAgc.checked && !c.missing_agc) return false;
    if (filterDelayedAm.checked && !c.am_delayed) return false;
    if (filterPm.value && c.pm !== filterPm.value) return false;
    if (filterCarteira.value && c.carteira !== filterCarteira.value) return false;
    if (filterRjPhase.value && c.rj_phase !== filterRjPhase.value) return false;
    if (filterClass.value && c.class !== filterClass.value) return false;
    if (filterStatus.value && c.status_tag !== filterStatus.value) return false;
    if (filterInvestigacao.value === "SIM" && c.am_delayed) return false;
    if (filterInvestigacao.value === "NAO" && !c.am_delayed) return false;
    if (filterDocsOk.value === "V" && c.has_missing_docs) return false;
    if (filterDocsOk.value === "X" && !c.has_missing_docs) return false;
    if (filterAgcOk.value === "OK" && c.missing_agc) return false;
    if (filterAgcOk.value === "N OK" && !c.missing_agc) return false;
    if (filterAgcWindow.value) {
      const hasDate = !!c.agc_date;
      const d = hasDate ? new Date(c.agc_date) : null;
      if (filterAgcWindow.value === "none" && hasDate) return false;
      if (filterAgcWindow.value === "next_30" && (!hasDate || d < now || d > plus30)) return false;
      if (filterAgcWindow.value === "next_month" && (!hasDate || d < nextMonthStart || d > nextMonthEnd)) return false;
      if (filterAgcWindow.value === "past" && (!hasDate || d >= now)) return false;
    }
    if (!matchTicket(c, filterTicket.value)) return false;
    if (search && !`${c.case_id} ${c.name}`.toLowerCase().includes(search)) return false;
    return true;
  });
}

function updateActiveFilterCount() {
  let n = 0;
  if (filterMissingDocs.checked) n++;
  if (filterMissingAgc.checked) n++;
  if (filterDelayedAm.checked) n++;
  [
    filterPm,
    filterCarteira,
    filterRjPhase,
    filterClass,
    filterStatus,
    filterInvestigacao,
    filterDocsOk,
    filterAgcOk,
    filterAgcWindow,
    filterTicket,
  ].forEach((el) => {
    if (el.value) n++;
  });
  if (filterSearch.value.trim()) n++;
  activeFiltersEl.textContent = `${n} filtro(s) ativos`;
}

function closeAllMenus() {
  document.querySelectorAll(".action-menu").forEach((m) => m.classList.add("hidden"));
}

function renderCases() {
  updateActiveFilterCount();
  const data = filteredCases();
  resultCount.textContent = `${data.length} resultado(s)`;

  casesBody.innerHTML = data
    .map(
      (c, idx) => `
      <tr>
        <td>${c.case_id}</td>
        <td>${c.name}</td>
        <td>${c.pm}</td>
        <td>${c.carteira}</td>
        <td>${currencyBRL.format(c.valor_credito)}</td>
        <td><span class="badge warn">${c.status_tag}</span></td>
        <td><span class="badge ${c.am_delayed ? "danger" : "ok"}">${c.am_update_tag}</span></td>
        <td><span class="badge ${c.am_delayed ? "danger" : "ok"}">${c.am_delayed ? "NAO" : "SIM"}</span></td>
        <td><span class="badge ${c.has_missing_docs ? "danger" : "ok"}">${c.has_missing_docs ? "X" : "V"}</span></td>
        <td><span class="badge ${c.missing_agc ? "danger" : "ok"}">${c.missing_agc ? "N OK" : "OK"}</span></td>
        <td>${fmtDate(c.agc_date)}</td>
        <td><span class="badge ${c.has_missing_docs ? "warn" : "ok"}">${c.has_missing_docs ? `${c.documentos_faltando.length} doc(s)` : "OK"}</span></td>
        <td>
          <div class="action-menu-wrap">
            <button class="action-menu-btn" data-menu-btn="${idx}">...</button>
            <div class="action-menu hidden" data-menu="${idx}">
              <button class="action-item" data-action="details" data-case-index="${idx}">Detalhes</button>
              <button class="action-item" data-action="docs" data-case-index="${idx}">Documentos</button>
              <button class="action-item" data-action="edit" data-case-index="${idx}">Editar</button>
              <button class="action-item" data-action="upload" data-case-index="${idx}">Upload doc</button>
            </div>
          </div>
        </td>
      </tr>`
    )
    .join("") || `<tr><td colspan="13">Nenhum caso encontrado com esse filtro.</td></tr>`;

  document.querySelectorAll("[data-menu-btn]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = btn.dataset.menuBtn;
      const menu = document.querySelector(`[data-menu="${id}"]`);
      const isHidden = menu.classList.contains("hidden");
      closeAllMenus();
      if (isHidden) menu.classList.remove("hidden");
    });
  });

  document.querySelectorAll(".action-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      const c = data[Number(btn.dataset.caseIndex)];
      closeAllMenus();
      if (btn.dataset.action === "details") openModal(c);
      if (btn.dataset.action === "docs") openDocsModal(c);
      if (btn.dataset.action === "edit") openEditModal(c);
      if (btn.dataset.action === "upload") openUploadModal(c);
    });
  });
}

function renderPhasesBoard() {
  const groups = {};
  const total = allCases.length || 1;
  allCases.forEach((c) => {
    if (!groups[c.rj_phase]) groups[c.rj_phase] = [];
    groups[c.rj_phase].push(c);
  });

  phasesBoard.innerHTML = Object.entries(groups)
    .sort((a, b) => b[1].length - a[1].length)
    .map(
      ([phase, cases]) => `
      <article class="phase-col">
        <div class="phase-header">
          <div class="phase-title-row">
            <span>${phase}</span>
            <span class="phase-count-badge">${cases.length} caso(s)</span>
          </div>
          <div class="phase-stats">
            <span>Participacao: ${Math.round((cases.length / total) * 100)}%</span>
            <span>Credito: ${currencyBRL.format(cases.reduce((acc, item) => acc + item.valor_credito, 0))}</span>
          </div>
          <div class="phase-progress"><span style="width:${Math.round((cases.length / total) * 100)}%"></span></div>
        </div>
        <div class="phase-list">
          ${cases
            .sort((a, b) => b.valor_credito - a.valor_credito)
            .map(
              (c) => `<div class="phase-card">
                <div class="title">${c.case_id} - ${c.name}</div>
                <div class="meta-row">
                  <div class="meta">PM ${c.pm}</div>
                  <div class="meta">${currencyBRL.format(c.valor_credito)}</div>
                </div>
                <div class="meta">AGC: ${fmtDate(c.agc_date)}</div>
                <div class="phase-chip-row">
                  <span class="badge ${c.am_delayed ? "danger" : "ok"}">${c.am_update_tag}</span>
                  <span class="badge ${c.has_missing_docs ? "warn" : "ok"}">${c.has_missing_docs ? `${c.documentos_faltando.length} doc(s)` : "Docs OK"}</span>
                </div>
              </div>`
            )
            .join("")}
        </div>
      </article>`
    )
    .join("");
}

function monthName(date) {
  return date.toLocaleDateString("pt-BR", { month: "long", year: "numeric" });
}

function renderAgcCalendarModal() {
  const year = calendarViewDate.getFullYear();
  const month = calendarViewDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startWeekday = (firstDay.getDay() + 6) % 7;
  const totalDays = lastDay.getDate();
  const agcMap = {};
  allCases.forEach((c) => {
    if (!c.agc_date) return;
    const d = new Date(c.agc_date);
    if (d.getFullYear() === year && d.getMonth() === month) {
      const day = d.getDate();
      if (!agcMap[day]) agcMap[day] = [];
      agcMap[day].push(c);
    }
  });

  agcCalTitle.textContent = monthName(calendarViewDate);
  const cells = [];
  for (let i = 0; i < startWeekday; i++) cells.push(`<div class="agc-cal-cell is-empty"></div>`);
  for (let day = 1; day <= totalDays; day++) {
    const hasAgc = !!agcMap[day];
    const isSelected =
      calendarSelectedDate &&
      calendarSelectedDate.getFullYear() === year &&
      calendarSelectedDate.getMonth() === month &&
      calendarSelectedDate.getDate() === day;
    cells.push(`<button class="agc-cal-cell ${isSelected ? "is-selected" : ""}" data-cal-day="${day}">
      <span class="agc-cal-day">${day}</span>
      ${hasAgc ? '<span class="agc-dot"></span>' : ""}
    </button>`);
  }
  agcCalGrid.innerHTML = cells.join("");

  agcCalGrid.querySelectorAll("[data-cal-day]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const day = Number(btn.dataset.calDay);
      calendarSelectedDate = new Date(year, month, day);
      const events = agcMap[day] || [];
      agcCalDayList.innerHTML = events.length
        ? events.map((c) => `<li>${c.case_id} - ${c.name} (${fmtDate(c.agc_date)})</li>`).join("")
        : "<li>Sem AGC neste dia.</li>";
      renderAgcCalendarModal();
    });
  });
}

function renderAgcView() {
  const withDate = allCases.filter((c) => !!c.agc_date).sort((a, b) => new Date(a.agc_date) - new Date(b.agc_date));
  const noDate = allCases.filter((c) => !c.agc_date);

  const today = new Date();
  const nextMonthStart = new Date(today.getFullYear(), today.getMonth() + 1, 1);
  const nextMonthEnd = new Date(today.getFullYear(), today.getMonth() + 2, 0);

  const nextMonthCases = withDate.filter((c) => {
    const d = new Date(c.agc_date);
    return d >= nextMonthStart && d <= nextMonthEnd;
  });

  agcNextCount.textContent = `AGCs no proximo mes: ${nextMonthCases.length}`;
  agcMissingCount.textContent = `Casos sem AGC definida: ${noDate.length}`;

  agcTimeline.innerHTML = withDate
    .map(
      (c) => `<article class="agc-item"><div class="agc-date">${fmtDate(c.agc_date)}</div><div><div class="agc-case">${c.case_id} - ${c.name}</div><div class="meta">${c.carteira} | PM ${c.pm} | Fase: ${c.rj_phase}</div></div></article>`
    )
    .join("");

  const monthBuckets = {};
  withDate.forEach((c) => {
    const d = new Date(c.agc_date);
    const key = `${d.getFullYear()}-${d.getMonth()}`;
    if (!monthBuckets[key]) monthBuckets[key] = { date: new Date(d.getFullYear(), d.getMonth(), 1), cases: [] };
    monthBuckets[key].cases.push(c);
  });

  agcCalendar.innerHTML = Object.values(monthBuckets)
    .sort((a, b) => a.date - b.date)
    .map(
      (bucket) => `<article class="calendar-month">
        <div class="calendar-head">${monthName(bucket.date)}</div>
        <div class="calendar-body">
          ${bucket.cases
            .sort((a, b) => new Date(a.agc_date) - new Date(b.agc_date))
            .map(
              (c) => `<div class="calendar-event"><div class="agc-date">${fmtDate(c.agc_date)}</div><div class="agc-case">${c.case_id} - ${c.name}</div><div class="meta">${c.rj_phase}</div></div>`
            )
            .join("")}
        </div>
      </article>`
    )
    .join("");

  if (agcMode === "timeline") {
    agcTimeline.classList.remove("hidden");
    agcCalendar.classList.add("hidden");
  } else {
    agcTimeline.classList.add("hidden");
    agcCalendar.classList.remove("hidden");
  }
}

function openModal(c) {
  modalTitle.textContent = `${c.case_id} - ${c.name}`;
  modalSubtitle.textContent = `${c.carteira} | PM ${c.pm} | Fase: ${c.rj_phase}`;
  const summary = [
    ["Valor Credito", currencyBRL.format(c.valor_credito)],
    ["QGC Total", `${numberFmt.format(c.qgc_total_mm)} MM`],
    ["PnL Target", `${c.pnl_target}%`],
    ["PnL sem NP", `${c.pnl_sem_np}%`],
    ["AGC", fmtDate(c.agc_date)],
    ["AM Update", c.am_update_tag],
    ["Classe", c.class],
    ["Status", c.status_tag],
  ];
  modalKpis.innerHTML = summary.map(([k, v]) => `<div class="modal-kpi"><div class="key">${k}</div><div class="val">${v}</div></div>`).join("");

  const details = {
    Face_MM: c.face_mm,
    QGC_MM: c.qgc_mm,
    Cost_MM: c.cost_mm,
    MtM_MM: c.mtm_mm,
    ERV_MM: c.erv_mm,
    NPV_MM: c.npv_mm,
    Prazo_Est_Y: c.prazo_estimado_anos,
    Prazo_Rema_Y: c.prazo_remanescente_anos,
    Pct_Class_I: `${c.pct_class_i}%`,
    Pct_Class_II: `${c.pct_class_ii}%`,
    Pct_Class_III: `${c.pct_class_iii}%`,
    Valor_Extra: currencyBRL.format(c.valor_extra),
  };
  modalGrid.innerHTML = Object.entries(details).map(([k, v]) => `<div class="modal-item"><div class="key">${k}</div><div class="val">${v}</div></div>`).join("");
  modalDocs.innerHTML = c.documentos_faltando.length ? c.documentos_faltando.map((d) => `<li>${d}</li>`).join("") : "<li>Nenhum documento pendente.</li>";
  modal.classList.remove("hidden");
}

function fakeDownload(fileName, caseId) {
  const content = `Arquivo mockado: ${fileName}\nCase: ${caseId}\nGerado em: ${new Date().toISOString()}`;
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName.replace(".pdf", ".txt");
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function openDocsModal(c) {
  docsModalTitle.textContent = `${c.case_id} - ${c.name}`;
  docsList.innerHTML = c.documentos_presentes.length
    ? c.documentos_presentes
        .map(
          (doc) => `<article class="doc-card">
            <div class="doc-title">${doc.sigla}</div>
            <div class="doc-meta">${doc.nome}</div>
            <button class="btn" data-download="${doc.arquivo}" data-case="${c.case_id}">Baixar ${doc.arquivo}</button>
          </article>`
        )
        .join("")
    : "<p>Nenhum documento presente.</p>";

  docsList.querySelectorAll("[data-download]").forEach((btn) => {
    btn.addEventListener("click", () => fakeDownload(btn.dataset.download, btn.dataset.case));
  });

  docsModal.classList.remove("hidden");
}

function openEditModal(c) {
  selectedCaseId = c.case_id;
  editModalTitle.textContent = `${c.case_id} - ${c.name}`;
  document.getElementById("edit-name").value = c.name || "";
  document.getElementById("edit-pm").value = c.pm || "";
  document.getElementById("edit-carteira").value = c.carteira || "";
  const rjPhaseSelect = document.getElementById("edit-rj-phase");
  const statusSelect = document.getElementById("edit-status");
  if (![...rjPhaseSelect.options].some((o) => o.value === c.rj_phase)) {
    rjPhaseSelect.add(new Option(c.rj_phase, c.rj_phase));
  }
  if (![...statusSelect.options].some((o) => o.value === c.status_tag)) {
    statusSelect.add(new Option(c.status_tag, c.status_tag));
  }
  rjPhaseSelect.value = c.rj_phase || "";
  statusSelect.value = c.status_tag || "";
  document.getElementById("edit-am-update").value = c.am_update_tag || "";
  document.getElementById("edit-agc-date").value = c.agc_date || "";
  document.getElementById("edit-valor").value = c.valor_credito || 0;
  editModal.classList.remove("hidden");
}

function openUploadModal(c) {
  selectedCaseId = c.case_id;
  uploadModalTitle.textContent = `${c.case_id} - ${c.name}`;
  uploadForm.reset();
  uploadModal.classList.remove("hidden");
}

function refreshDerivedFields(c) {
  c.has_missing_docs = c.documentos_faltando.length > 0;
  c.missing_agc = !c.agc_date;
  c.am_delayed = c.am_update_tag.toLowerCase().includes("atras") || c.am_update_tag.includes("15+");
}

function clearFilters() {
  filterMissingDocs.checked = false;
  filterMissingAgc.checked = false;
  filterDelayedAm.checked = false;
  filterPm.value = "";
  filterCarteira.value = "";
  filterRjPhase.value = "";
  filterClass.value = "";
  filterStatus.value = "";
  filterInvestigacao.value = "";
  filterDocsOk.value = "";
  filterAgcOk.value = "";
  filterAgcWindow.value = "";
  filterTicket.value = "";
  filterSearch.value = "";
  renderCases();
}

function setupViews() {
  const navButtons = document.querySelectorAll(".nav-item");
  const views = document.querySelectorAll(".view");
  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      navButtons.forEach((b) => b.classList.remove("active"));
      views.forEach((v) => v.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.view).classList.add("active");
    });
  });
}

function setupAgcModeToggle() {
  document.querySelectorAll(".agc-mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".agc-mode-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      agcMode = btn.dataset.agcMode;
      renderAgcView();
    });
  });
}

toggleSidebarBtn.addEventListener("click", () => {
  layout.classList.toggle("sidebar-collapsed");
});

document.addEventListener("click", () => closeAllMenus());

closeModalBtn.addEventListener("click", () => modal.classList.add("hidden"));
modal.addEventListener("click", (event) => {
  if (event.target === modal) modal.classList.add("hidden");
});
closeDocsModalBtn.addEventListener("click", () => docsModal.classList.add("hidden"));
docsModal.addEventListener("click", (event) => {
  if (event.target === docsModal) docsModal.classList.add("hidden");
});
closeEditModalBtn.addEventListener("click", () => editModal.classList.add("hidden"));
editModal.addEventListener("click", (event) => {
  if (event.target === editModal) editModal.classList.add("hidden");
});
closeUploadModalBtn.addEventListener("click", () => uploadModal.classList.add("hidden"));
uploadModal.addEventListener("click", (event) => {
  if (event.target === uploadModal) uploadModal.classList.add("hidden");
});
openAgcCalendarModalBtn.addEventListener("click", () => {
  calendarViewDate = new Date();
  calendarSelectedDate = null;
  agcCalDayList.innerHTML = "<li>Selecione um dia para ver os casos.</li>";
  renderAgcCalendarModal();
  agcCalendarModal.classList.remove("hidden");
});
closeAgcCalendarModalBtn.addEventListener("click", () => agcCalendarModal.classList.add("hidden"));
agcCalendarModal.addEventListener("click", (event) => {
  if (event.target === agcCalendarModal) agcCalendarModal.classList.add("hidden");
});
agcCalPrevBtn.addEventListener("click", () => {
  calendarViewDate = new Date(calendarViewDate.getFullYear(), calendarViewDate.getMonth() - 1, 1);
  calendarSelectedDate = null;
  agcCalDayList.innerHTML = "<li>Selecione um dia para ver os casos.</li>";
  renderAgcCalendarModal();
});
agcCalNextBtn.addEventListener("click", () => {
  calendarViewDate = new Date(calendarViewDate.getFullYear(), calendarViewDate.getMonth() + 1, 1);
  calendarSelectedDate = null;
  agcCalDayList.innerHTML = "<li>Selecione um dia para ver os casos.</li>";
  renderAgcCalendarModal();
});

editForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const c = allCases.find((item) => item.case_id === selectedCaseId);
  if (!c) return;
  c.name = document.getElementById("edit-name").value.trim();
  c.pm = document.getElementById("edit-pm").value.trim();
  c.carteira = document.getElementById("edit-carteira").value.trim();
  c.rj_phase = document.getElementById("edit-rj-phase").value.trim();
  c.status_tag = document.getElementById("edit-status").value.trim();
  c.am_update_tag = document.getElementById("edit-am-update").value.trim();
  c.agc_date = document.getElementById("edit-agc-date").value.trim() || null;
  c.valor_credito = Number(document.getElementById("edit-valor").value || 0);
  refreshDerivedFields(c);
  editModal.classList.add("hidden");
  renderCases();
  renderPhasesBoard();
  renderAgcView();
});

uploadForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const c = allCases.find((item) => item.case_id === selectedCaseId);
  if (!c) return;
  const docType = document.getElementById("upload-doc-type").value;
  const fileInput = document.getElementById("upload-file");
  const fileName = fileInput.files[0] ? fileInput.files[0].name : `${c.case_id}_${docType}.pdf`;
  c.documentos_presentes.push({
    id: `${c.case_id}-${docType}-${Date.now()}`,
    sigla: docType,
    nome: docType,
    arquivo: fileName,
  });
  c.documentos_faltando = c.documentos_faltando.filter((d) => !d.toUpperCase().includes(docType));
  refreshDerivedFields(c);
  uploadModal.classList.add("hidden");
  renderCases();
});

[
  filterMissingDocs,
  filterMissingAgc,
  filterDelayedAm,
  filterPm,
  filterCarteira,
  filterRjPhase,
  filterClass,
  filterStatus,
  filterInvestigacao,
  filterDocsOk,
  filterAgcOk,
  filterAgcWindow,
  filterTicket,
].forEach((filterEl) => filterEl.addEventListener("change", renderCases));

filterSearch.addEventListener("input", renderCases);
clearFiltersBtn.addEventListener("click", clearFilters);
setupViews();
setupAgcModeToggle();

fetch("/api/dashboard")
  .then((res) => res.json())
  .then((data) => {
    allCases = data.cases;
    buildKpis(data.kpis);
    setupFilterOptions();
    renderCases();
    renderPhasesBoard();
    renderAgcView();
    refDate.textContent = `Referencia: ${fmtDate(data.reference_date)}`;
  });
