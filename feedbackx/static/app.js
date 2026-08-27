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
    titleRoadmap: "Prioritized Feature Roadmap (RICE Matrix)"
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
    titleRoadmap: "خارطة طريق المزايا ذات الأولوية (نموذج RICE)"
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

function init() {
  renderPresets();
  runFeedbackMining();
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
  bar.innerHTML = `
    <span class="pipe-tag">Reviews: ${data.total_reviews_analyzed} Analyzed</span>
    <span class="pipe-tag">Aspects: ${data.aspect_clusters.length} Clustered</span>
    <span class="pipe-tag">Top RICE: ${data.prioritized_roadmap[0].rice_score}</span>
    <span class="pipe-tag">P0 Items: ${data.prioritized_roadmap.filter(i => i.urgency_tier === 'P0_IMMEDIATE').length}</span>
  `;

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

window.addEventListener('DOMContentLoaded', init);
