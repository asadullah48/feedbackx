// FeedbackX Interactive Controller & Bilingual Localization

let currentLang = 'en';

const TRANSLATIONS = {
  en: {
    badgeTitle: "Customer Intelligence",
    statusLive: "Review Mining Pipeline Active (:8020)",
    heroTitle: "Mining Thousands of Customer Reviews into Prioritized Product Roadmaps",
    heroSubtitle: "Eradicate customer churn with ScraperAgent (5+ channel review ingestion), AnalyzerAgent (Aspect-Based Sentiment Analysis), and InsightAgent (automated RICE roadmap prioritization).",
    metric1Label: "Reviews Scraped",
    metric1Sub: "App Store, G2 & Trustpilot",
    metric2Label: "Top Churn Friction",
    metric2Sub: "88.5% Churn Risk Score",
    metric3Label: "Top RICE Score",
    metric3Sub: "High Strategic ROI",
    metric4Label: "Churn Reduction",
    metric4Sub: "Projected Post-Release",
    studioTitle: "Customer Intelligence & RICE Roadmap Studio",
    studioDesc: "Aggregate customer review streams, identify feature gaps and pain points, and generate an executive product roadmap.",
    lblPresets: "Select Market Intelligence Preset:",
    lblReviewVolume: "Review Ingestion Volume",
    btnExecuteMine: "💬 Ingest Reviews & Synthesize RICE Roadmap",
    titleRoadmap: "Prioritized Feature Roadmap (RICE Matrix)",
    titleSummary: "Executive Strategic Summary",
    llmChecking: "Checking LLM…",
    llmOff: "Deterministic Mode (LLM Off)",
    llmActive: "Ollama LLM Active",
    llmUnreachable: "Ollama Configured (Unreachable)"
  },
  ar: {
    badgeTitle: "استخبارات آراء العملاء",
    statusLive: "محرك تحليل التقييمات نشط (:8020)",
    heroTitle: "تحويل آلاف تقييمات العملاء إلى خارطة طريق برمجية ذات أولوية",
    heroSubtitle: "تقليل معدلات تراجع العملاء مع ScraperAgent (جمع التقييمات من 5 قنوات)، و AnalyzerAgent (تحليل المشاعر الدقيق ABSA)، و InsightAgent (أولويات RICE الذكية).",
    metric1Label: "التقييمات المجمعة",
    metric1Sub: "متاجر التطبيقات و G2 و Trustpilot",
    metric2Label: "أكبر سبب للتراجع",
    metric2Sub: "غياب صلاحيات RBAC (88.5%)",
    metric3Label: "أعلى درجة RICE",
    metric3Sub: "عائد استراتيجي مرتفع",
    metric4Label: "خفض التراجع المتوقع",
    metric4Sub: "بعد إطلاق التحديثات",
    studioTitle: "استوديو استخبارات آراء العملاء وخارطة RICE",
    studioDesc: "تجميع تدفقات التقييمات، واكتشاف الفجوات البرمجية، وتوليد خارطة طريق تنفيذية ذات أولوية واضحة.",
    lblPresets: "اختر سيناريو استخبارات مسبق:",
    lblReviewVolume: "حجم التقييمات المجمعة",
    btnExecuteMine: "💬 تجميع التقييمات وصياغة خارطة RICE",
    titleRoadmap: "خارطة طريق المزايا ذات الأولوية (نموذج RICE)",
    titleSummary: "الملخص الاستراتيجي التنفيذي",
    llmChecking: "جارِ التحقق من نموذج اللغة…",
    llmOff: "الوضع الحتمي (نموذج اللغة متوقف)",
    llmActive: "نموذج Ollama نشط",
    llmUnreachable: "تم تفعيل Ollama لكنه غير متاح"
  }
};

const SCENARIOS = [
  {
    name: "🏢 B2B SaaS Enterprise Platform (1,500 Reviews)",
    volume: "1500"
  },
  {
    name: "📱 Consumer Mobile App (3,000 Reviews)",
    volume: "3000"
  },
  {
    name: "⚡ Developer Productivity Tool (500 Reviews)",
    volume: "500"
  }
];

let lastLlmStatus = null;

function init() {
  renderPresets();
  checkLlmStatus();
  runFeedbackMining();
}

async function checkLlmStatus() {
  try {
    const res = await fetch('/api/v1/system/llm-status');
    lastLlmStatus = await res.json();
  } catch (err) {
    console.error("Error checking LLM status:", err);
    lastLlmStatus = { enabled: false, available: false, model: null };
  }
  renderLlmStatus();
}

function renderLlmStatus() {
  const dot = document.querySelector('#llmStatus .pulse-dot');
  const label = document.getElementById('llmStatusLabel');
  const t = TRANSLATIONS[currentLang];
  if (!lastLlmStatus) {
    label.innerText = t.llmChecking;
    return;
  }
  if (!lastLlmStatus.enabled) {
    label.innerText = t.llmOff;
    dot.className = 'pulse-dot muted';
  } else if (lastLlmStatus.available) {
    label.innerText = `${t.llmActive} (${lastLlmStatus.model})`;
    dot.className = 'pulse-dot active';
  } else {
    label.innerText = t.llmUnreachable;
    dot.className = 'pulse-dot';
  }
}

function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'ar' : 'en';
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
  document.getElementById('langLabel').innerText = currentLang === 'en' ? 'العربية' : 'English';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (TRANSLATIONS[currentLang][key]) {
      el.innerText = TRANSLATIONS[currentLang][key];
    }
  });

  renderLlmStatus();
}

function renderPresets() {
  const container = document.getElementById('scenarioButtons');
  container.innerHTML = '';
  SCENARIOS.forEach((sc, idx) => {
    const btn = document.createElement('button');
    btn.className = 'preset-btn';
    btn.innerText = sc.name;
    btn.onclick = () => loadScenario(idx);
    container.appendChild(btn);
  });
}

function loadScenario(idx) {
  const sc = SCENARIOS[idx];
  document.getElementById('volumeSelect').value = sc.volume;
  runFeedbackMining();
}

async function runFeedbackMining() {
  const btn = document.getElementById('mineBtn');
  const count = parseInt(document.getElementById('volumeSelect').value);

  btn.disabled = true;
  btn.innerText = "Ingesting Reviews -> Running ABSA Analysis -> Computing RICE Scores...";

  try {
    const res = await fetch(`/api/v1/feedback/generate-intelligence?review_count=${count}`, {
      method: 'POST'
    });

    const data = await res.json();
    renderRoadmapResult(data);

  } catch (err) {
    console.error("Error mining feedback:", err);
  } finally {
    btn.disabled = false;
    btn.innerText = TRANSLATIONS[currentLang].btnExecuteMine;
  }
}

function renderRoadmapResult(data) {
  const bar = document.getElementById('pipelineBar');
  const topRoadmap = data.prioritized_roadmap[0] || null;
  bar.innerHTML = `
    <span class="pipe-tag">Reviews: ${data.total_reviews_analyzed} Analyzed</span>
    <span class="pipe-tag">Aspects: ${data.aspect_clusters.length} Clustered</span>
    <span class="pipe-tag">Top RICE: ${topRoadmap ? topRoadmap.rice_score : '—'}</span>
    <span class="pipe-tag">P0 Items: ${data.prioritized_roadmap.filter(i => i.urgency_tier === 'P0_IMMEDIATE').length}</span>
  `;

  renderMetrics(data);

  const summaryEl = document.getElementById('summaryText');
  if (summaryEl) {
    summaryEl.innerText = data.executive_strategic_summary || '—';
  }

  const container = document.getElementById('roadmapList');
  container.innerHTML = '';
  data.prioritized_roadmap.forEach(item => {
    const card = document.createElement('div');
    card.className = 'roadmap-card';
    card.innerHTML = `
      <div class="roadmap-header">
        <span class="roadmap-title">${item.feature_title}</span>
        <span class="roadmap-rice">RICE: ${item.rice_score} • ${item.urgency_tier}</span>
      </div>
      <p class="roadmap-body">${item.pain_point_addressed}</p>
      <div class="roadmap-meta">
        <span>Est. Churn Reduction: -${item.estimated_churn_reduction_percent}%</span>
        <span>High Impact Vector</span>
      </div>
    `;
    container.appendChild(card);
  });
}

const TIER_LABELS = { P0_IMMEDIATE: 'P0', P1_NEXT_SPRINT: 'P1', P2_BACKLOG: 'P2' };

function renderMetrics(data) {
  const topChurnCluster = data.aspect_clusters[0] || null;      // pre-sorted by churn_risk_score desc
  const topRoadmapItems = data.prioritized_roadmap.slice(0, 3); // pre-sorted by rice_score desc
  const churnReduction = topRoadmapItems.reduce((sum, i) => sum + i.estimated_churn_reduction_percent, 0);

  setText('metricReviews', `${data.total_reviews_analyzed} Items`);
  setText('metricChurnAspect', topChurnCluster ? topChurnCluster.aspect_name : 'N/A');
  setText('metricChurnScore', topChurnCluster ? `${topChurnCluster.churn_risk_score.toFixed(1)}% Churn Risk Score` : 'No churn signal');
  setText('metricTopRice', topRoadmapItems[0] ? `${topRoadmapItems[0].rice_score} (${TIER_LABELS[topRoadmapItems[0].urgency_tier] || topRoadmapItems[0].urgency_tier})` : 'N/A');
  setText('metricChurnReduction', `-${churnReduction.toFixed(1)}% Churn`);
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

window.addEventListener('DOMContentLoaded', init);
