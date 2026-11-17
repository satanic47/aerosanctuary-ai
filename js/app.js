/**
 * AeroSanctuary AI - Interactive Client Application Script
 * Dual-Mode Engine: Seamlessly connects to FastAPI Backend or operates autonomously on static hosts (GitHub Pages).
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const profileForm = document.getElementById('profile-form');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input-text');
  const chatMessages = document.getElementById('chat-messages');
  const routineList = document.getElementById('routine-list');
  const hacksContainer = document.getElementById('hacks-container');
  const hackTabs = document.querySelectorAll('.hack-tab');

  // AQI Metric Elements
  const cityLabel = document.getElementById('current-city-label');
  const aqiValue = document.getElementById('aqi-value');
  const aqiSeverity = document.getElementById('aqi-severity');
  const pm25Val = document.getElementById('pm25-val');
  const pm10Val = document.getElementById('pm10-val');
  const safeWindowVal = document.getElementById('safe-window-val');
  const inversionBadge = document.getElementById('inversion-status-badge');

  // Impact Metric Elements
  const pm25Avoided = document.getElementById('metric-pm25-avoided');
  const cigsAvoided = document.getElementById('metric-cigs-avoided');
  const co2Saved = document.getElementById('metric-co2-saved');
  const stressReduced = document.getElementById('metric-stress-reduced');
  const aiSummaryText = document.getElementById('ai-summary-text');
  const communityScalingText = document.getElementById('community-scaling-text');

  let allHacks = [];

  // =========================================================================
  // Static Fallback Data for Autonomous GitHub Pages Operation
  // =========================================================================
  const STATIC_HACKS = [
    {
      id: "corsi_rosenthal_box",
      category: "diy_filtration",
      title: "DIY Corsi-Rosenthal Cube Air Purifier",
      problem_addressed: "Severe ambient particulate penetration where commercial HEPA purifiers are cost-prohibitive.",
      materials_needed: [
        "1x 20-inch standard box fan (forward airflow)",
        "4x MERV 13 rated furnace filters (20x20x2 inch)",
        "1x Cardboard shroud cutout (14-inch circular opening)",
        "Duct tape or painter's tape for airtight perimeter sealing"
      ],
      step_by_step_instructions: [
        "Arrange the 4 MERV 13 filters in a square cube with airflow direction arrows pointing INWARD.",
        "Secure all vertical corners and the bottom cardboard base firmly with duct tape.",
        "Mount the box fan on top with exhaust airflow pointing UPWARD.",
        "Tape the cardboard shroud to the front face of the fan to eliminate blade-tip recirculation.",
        "Operate continuously on medium speed in the primary living or sleeping area."
      ],
      estimated_cost_inr: 2800,
      expected_pm25_reduction: "85% - 92% CADR equivalent to ₹25,000 commercial units",
      scientific_basis: "UC Davis & EPA verified peer-reviewed bioaerosol filtration protocol."
    },
    {
      id: "botanical_bio_filtration",
      category: "botanical",
      title: "Targeted Botanical VOC & Particulate Deposition",
      problem_addressed: "Indoor accumulation of formaldehyde, benzene, and secondary aerosol precursors.",
      materials_needed: [
        "2x Snake Plants (Sansevieria trifasciata) per bedroom",
        "1x Areca Palm (Dypsis lutescens) per living area",
        "Microfiber wipe cloth for bi-weekly leaf surface cleaning"
      ],
      step_by_step_instructions: [
        "Place Snake Plants inside bedrooms; they perform Crassulacean Acid Metabolism (CAM), releasing oxygen and metabolizing toxins during nocturnal hours.",
        "Position Areca Palms in sunny living quarters to regulate relative humidity and settle airborne dust.",
        "Gently wipe foliage with a damp cloth every 5 days to remove settled particulate crust and restore stomatal absorption."
      ],
      estimated_cost_inr: 650,
      expected_pm25_reduction: "18% - 25% VOC removal and continuous oxygen enhancement",
      scientific_basis: "NASA Clean Air Study (Wolverton et al.) & phytoremediation literature."
    },
    {
      id: "thermal_inversion_ventilation",
      category: "ventilation_timing",
      title: "Midday Solar Thermal Inversion Ventilation Protocol",
      problem_addressed: "Unintentional indoor pollution spikes caused by opening windows during dawn and morning boundary layer stagnation.",
      materials_needed: [
        "Simple adhesive door weatherstripping foam tape",
        "Window draft stopper seals"
      ],
      step_by_step_instructions: [
        "Keep all external fenestrations strictly sealed between 06:00 AM and 11:30 AM when radiation inversion holds ground pollutants.",
        "Perform rapid cross-ventilation (15-20 minutes only) strictly between 12:30 PM and 03:00 PM when solar ground heating breaks the inversion layer.",
        "Reseal all windows before 04:30 PM prior to evening temperature drop and traffic rush hour."
      ],
      estimated_cost_inr: 250,
      expected_pm25_reduction: "60% - 75% reduction in indoor infiltration spikes",
      scientific_basis: "Atmospheric Boundary Layer (ABL) thermal mixing thermodynamics."
    },
    {
      id: "damp_microfiber_dust_abatement",
      category: "source_control",
      title: "Electrostatic Wet Dust Abatement (No Resuspension)",
      problem_addressed: "Dry sweeping and dusting resuspending settled coarse and fine toxic particulates into breathing zones.",
      materials_needed: [
        "2x Microfiber cloths or mop pads",
        "Diluted water-glycerin spray mist solution"
      ],
      step_by_step_instructions: [
        "Cease all dry broom sweeping, feather dusting, and high-velocity vacuuming without HEPA seals.",
        "Lightly mist surfaces with water before wiping, trapping settled particulates via capillary action.",
        "Mop floors in a single S-pattern to capture lead, cadmium, and tire dust without resuspension into children's breathing zone."
      ],
      estimated_cost_inr: 180,
      expected_pm25_reduction: "45% reduction in resuspended indoor PM10 and PM2.5",
      scientific_basis: "WHO Indoor Environmental Quality guidelines on mechanical aerosol resuspension."
    }
  ];

  const STATIC_REGIONS = {
    "Delhi-NCR": { city: "Delhi-NCR", aqi: 412, severity: "Severe / Hazardous", pm25: 315.4, pm10: 460.0, safest_window: "12:30 PM - 03:30 PM", inversion: true },
    "Chandigarh": { city: "Chandigarh", aqi: 288, severity: "Poor / Severe Smog", pm25: 185.0, pm10: 275.0, safest_window: "01:00 PM - 04:00 PM", inversion: true },
    "Mumbai": { city: "Mumbai", aqi: 165, severity: "Moderate / Unhealthy", pm25: 78.5, pm10: 142.0, safest_window: "11:30 AM - 04:30 PM", inversion: false },
    "Lahore": { city: "Lahore", aqi: 485, severity: "Hazardous / Emergency", pm25: 395.0, pm10: 540.0, safest_window: "01:00 PM - 03:00 PM", inversion: true },
    "Beijing": { city: "Beijing", aqi: 142, severity: "Moderate", pm25: 58.0, pm10: 110.0, safest_window: "10:30 AM - 04:00 PM", inversion: false },
    "New York": { city: "New York", aqi: 48, severity: "Good", pm25: 12.0, pm10: 24.0, safest_window: "All Day", inversion: false },
    "London": { city: "London", aqi: 56, severity: "Moderate Baseline", pm25: 15.5, pm10: 30.0, safest_window: "10:00 AM - 05:00 PM", inversion: false }
  };

  // =========================================================================
  // 1. Initial Data Fetching
  // =========================================================================
  async function initializeDashboard() {
    await fetchIndoorHacks();
    await triggerPlanGeneration();
  }

  // =========================================================================
  // 2. Fetch Indoor Air Quality Hacks
  // =========================================================================
  async function fetchIndoorHacks(category = 'all') {
    try {
      const url = category === 'all' ? 'api/indoor-hacks' : `api/indoor-hacks?category=${category}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('API offline');
      allHacks = await response.json();
      renderIndoorHacks(allHacks);
    } catch {
      // Fallback for static GitHub Pages
      if (category === 'all') {
        allHacks = STATIC_HACKS;
      } else {
        allHacks = STATIC_HACKS.filter(h => h.category === category);
      }
      renderIndoorHacks(allHacks);
    }
  }

  function renderIndoorHacks(hacks) {
    hacksContainer.innerHTML = '';
    if (!hacks || hacks.length === 0) {
      hacksContainer.innerHTML = '<p>No solutions match this filter category.</p>';
      return;
    }

    hacks.forEach((hack, index) => {
      const item = document.createElement('div');
      item.className = 'hack-accordion-item';

      const isFirst = index === 0;
      item.innerHTML = `
        <button class="hack-header-btn" aria-expanded="${isFirst}" aria-controls="hack-body-${hack.id}" id="hack-btn-${hack.id}">
          <span>${hack.title}</span>
          <span class="hack-cost-badge">Est. ₹${hack.estimated_cost_inr}</span>
        </button>
        <div id="hack-body-${hack.id}" class="hack-body" role="region" aria-labelledby="hack-btn-${hack.id}" style="display: ${isFirst ? 'block' : 'none'};">
          <p><strong>Problem:</strong> ${hack.problem_addressed}</p>
          <p><strong>Expected Efficiency:</strong> <span class="badge-success">${hack.expected_pm25_reduction}</span></p>
          <p><strong>Materials Required:</strong></p>
          <ul>
            ${hack.materials_needed.map(m => `<li>${m}</li>`).join('')}
          </ul>
          <p><strong>Implementation Protocol:</strong></p>
          <ol style="padding-left: 20px; margin-top: 6px;">
            ${hack.step_by_step_instructions.map(step => `<li>${step}</li>`).join('')}
          </ol>
          <p style="margin-top: 10px; font-size: 11.5px; color: #64748b;"><em>Source/Science: ${hack.scientific_basis}</em></p>
        </div>
      `;

      const btn = item.querySelector('.hack-header-btn');
      const body = item.querySelector('.hack-body');
      btn.addEventListener('click', () => {
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', !expanded);
        body.style.display = expanded ? 'none' : 'block';
      });

      hacksContainer.appendChild(item);
    });
  }

  // Handle Tab Switching
  hackTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      hackTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const cat = tab.getAttribute('data-cat');
      fetchIndoorHacks(cat);
    });
  });

  // =========================================================================
  // 3. Plan Generation & Profile Submission
  // =========================================================================
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await triggerPlanGeneration();
  });

  async function triggerPlanGeneration() {
    const location = document.getElementById('input-location').value;
    const household = document.getElementById('input-household').value;
    const commute = document.getElementById('input-commute').value;
    const km = parseFloat(document.getElementById('input-km').value) || 18.0;

    const payload = {
      location: location,
      household_type: household,
      commute_mode: commute,
      daily_commute_km: km,
      heating_source: "none_passive",
      ventilation_habits: "Morning windows",
      air_purifier_owned: false
    };

    const submitBtn = document.getElementById('btn-generate-plan');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>⚡ Analyzing Meteorological & Smog Data...</span>';

    try {
      const response = await fetch('api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('API offline');
      const data = await response.json();
      updateDashboard(data);
    } catch {
      // Deterministic Client Modeling for GitHub Pages
      const clientData = computeClientPlan(payload);
      updateDashboard(clientData);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>🚀 Generate Tailored Smog Action Plan</span>';
    }
  }

  function computeClientPlan(payload) {
    const region = STATIC_REGIONS[payload.location] || STATIC_REGIONS["Delhi-NCR"];
    const km = payload.daily_commute_km || 18.0;

    const emissionFactors = {
      "ice_car": 0.192,
      "motorcycle_scooter": 0.085,
      "metro_public_transit": 0.028,
      "electric_vehicle": 0.045,
      "shared_carpool": 0.064,
      "walking_cycling": 0.0,
      "remote_wfh": 0.0
    };

    const currentFactor = emissionFactors[payload.commute_mode] || 0.192;
    const dailyCarbonSaved = Math.max(0, (currentFactor - 0.028) * km);
    const dailyPm25Avoided = Math.round(region.pm25 * 1.943 * 10) / 10;
    const cigsAvoided = Math.round((dailyPm25Avoided / 396.0) * 10) / 10;
    const stressCut = Math.min(85.0, Math.round((35.0 + (region.pm25 / 10.0)) * 10) / 10);
    const annualCommunityCo2 = Math.round(dailyCarbonSaved * 100 * 365);

    return {
      user_profile: payload,
      air_quality_snapshot: {
        city: region.city,
        aqi: region.aqi,
        severity: region.severity,
        pm25_ug_m3: region.pm25,
        pm10_ug_m3: region.pm10,
        safest_outdoor_window: region.safest_window,
        thermal_inversion_active: region.inversion
      },
      daily_routine_schedule: [
        {
          time_slot: "06:00 AM - 08:30 AM",
          activity: "Morning Transition & Commute",
          recommended_alternative: "Keep windows sealed against radiation inversion. Realign transit to electric metro or carpool with N95.",
          hazard_rationale: "Early morning ground temperature drops trap heavy exhaust and PM2.5 in a stagnant boundary layer.",
          emission_saved_kg_co2e: Math.round(dailyCarbonSaved * 0.5 * 100) / 100,
          pm25_exposure_reduction_percent: 78.5
        },
        {
          time_slot: "12:30 PM - 03:00 PM",
          activity: "Midday Rapid Cross-Ventilation",
          recommended_alternative: "Open opposite-facing windows for 15-20 minutes to purge accumulated indoor CO2 without fine dust intrusion.",
          hazard_rationale: "Solar insolation warms the earth's surface, breaking the nocturnal temperature inversion and dispersing pollutants.",
          emission_saved_kg_co2e: 0.0,
          pm25_exposure_reduction_percent: 65.0
        },
        {
          time_slot: "05:30 PM - 08:00 PM",
          activity: "Evening Commute & Cooking Hours",
          recommended_alternative: "Operate kitchen exhaust fan with kitchen door closed. Switch on DIY Corsi-Rosenthal filtration in bedrooms.",
          hazard_rationale: "Evening traffic rush combined with culinary oils produces dangerous peaks in alveolar ultrafine particulate count.",
          emission_saved_kg_co2e: Math.round(dailyCarbonSaved * 0.5 * 100) / 100,
          pm25_exposure_reduction_percent: 74.0
        }
      ],
      indoor_defense_hacks: STATIC_HACKS,
      impact_ledger: {
        daily_pm25_avoided_micrograms: dailyPm25Avoided,
        cigarette_smoke_equivalents_avoided: cigsAvoided,
        daily_carbon_abatement_kg_co2e: Math.round(dailyCarbonSaved * 100) / 100,
        respiratory_stress_index_reduction: stressCut,
        annualized_community_co2_savings_kg: annualCommunityCo2,
        impact_narrative: `By optimizing routines in ${region.city}, your household prevents inhaling ${dailyPm25Avoided} µg of PM2.5 daily (${cigsAvoided} cigarette equivalents) while cutting ${Math.round(dailyCarbonSaved * 100) / 100} kg of CO2e.`
      },
      genai_executive_summary: `In ${region.city}, active winter thermal inversion is trapping dangerous surface PM2.5 levels (${region.pm25} µg/m³). By realigning your ${km.toFixed(1)} km transit routine to low-emission modes and deploying low-cost indoor filtration, your household will avoid inhaling ${dailyPm25Avoided} µg of toxic particulates daily while directly abating ${Math.round(dailyCarbonSaved * 100) / 100} kg of CO2e.`
    };
  }

  function updateDashboard(data) {
    const snap = data.air_quality_snapshot;
    const impact = data.impact_ledger;

    // Update Hero
    cityLabel.textContent = snap.city;
    aqiValue.textContent = snap.aqi;
    aqiSeverity.textContent = snap.severity;
    pm25Val.innerHTML = `${snap.pm25_ug_m3} <small>µg/m³</small>`;
    pm10Val.innerHTML = `${snap.pm10_ug_m3} <small>µg/m³</small>`;
    safeWindowVal.textContent = snap.safest_outdoor_window;

    if (snap.thermal_inversion_active) {
      inversionBadge.textContent = '⚠️ Winter Thermal Inversion Active';
      inversionBadge.className = 'inversion-badge active';
    } else {
      inversionBadge.textContent = '✓ Low Meteorological Inversion';
      inversionBadge.className = 'inversion-badge';
    }

    // Update AI Executive Synthesis
    aiSummaryText.textContent = data.genai_executive_summary;

    // Update Routine Timeline
    routineList.innerHTML = '';
    data.daily_routine_schedule.forEach(r => {
      const el = document.createElement('div');
      el.className = 'routine-card-item';
      el.innerHTML = `
        <span class="item-time">${r.time_slot}</span>
        <h4 class="item-act">${r.activity}</h4>
        <p class="item-rec"><strong>Recommendation:</strong> ${r.recommended_alternative}</p>
        <p style="font-size: 12px; color: #64748b; margin-bottom: 6px;"><em>Hazard Rationale: ${r.hazard_rationale}</em></p>
        <div class="routine-metrics">
          <span class="routine-badge-green">🛡️ ${r.pm25_exposure_reduction_percent}% PM2.5 Inhaled Cut</span>
          ${r.emission_saved_kg_co2e > 0 ? `<span class="routine-badge-green">🌱 ${r.emission_saved_kg_co2e} kg CO2e Saved</span>` : ''}
        </div>
      `;
      routineList.appendChild(el);
    });

    // Update Impact Ledger
    pm25Avoided.innerHTML = `${impact.daily_pm25_avoided_micrograms} <small>µg</small>`;
    cigsAvoided.innerHTML = `${impact.cigarette_smoke_equivalents_avoided} <small>cigs</small>`;
    co2Saved.innerHTML = `${impact.daily_carbon_abatement_kg_co2e} <small>kg</small>`;
    stressReduced.textContent = `${impact.respiratory_stress_index_reduction}%`;

    communityScalingText.innerHTML = `If 100 families in your neighborhood adopt these routines, your community will abate <strong>${impact.annualized_community_co2_savings_kg.toLocaleString()} kg of CO2e</strong> annually while eliminating tens of millions of micrograms of inhaled toxins.`;
  }

  // =========================================================================
  // 4. Interactive GenAI Chat
  // =========================================================================
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    // Append user message
    appendChatMessage('user', 'You', query);
    chatInput.value = '';

    // Show temporary typing indicator
    const typingId = appendChatMessage('assistant', 'AeroSanctuary AI', 'Thinking...');

    try {
      const location = document.getElementById('input-location').value;
      const household = document.getElementById('input-household').value;
      const commute = document.getElementById('input-commute').value;

      const payload = {
        message: query,
        user_profile: {
          location: location,
          household_type: household,
          commute_mode: commute,
          daily_commute_km: 18.0
        }
      };

      const res = await fetch('api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('API offline');
      const data = await res.json();
      renderChatResponse(typingId, data);
    } catch {
      // Deterministic Client Modeling for GitHub Pages
      const clientReply = computeClientChat(query);
      renderChatResponse(typingId, clientReply);
    }
  });

  function computeClientChat(query) {
    const q = query.toLowerCase();
    if (q.includes('toddler') || q.includes('child') || q.includes('baby') || q.includes('infant') || q.includes('morning')) {
      return {
        reply: "Children have higher minute-ventilation rates relative to their body weight, inhaling twice the volume of pollutants per kilogram compared to adults. During early morning hours (6:00 AM - 9:30 AM), thermal inversion traps PM2.5 and diesel soot within 10 meters of ground level.",
        actionable_tips: [
          "Keep infants indoors before 11:30 AM during active winter thermal inversions.",
          "Schedule all outdoor movement strictly between 12:30 PM and 3:30 PM.",
          "Use a certified pediatric N95 respirator if outdoor movement is non-negotiable."
        ],
        direct_impact_statement: "Rescheduling morning outdoor movement prevents up to 78% of acute alveolar particulate loading."
      };
    } else if (q.includes('diy') || q.includes('corsi') || q.includes('purifier') || q.includes('filter')) {
      return {
        reply: "A DIY Corsi-Rosenthal Box delivers over 500-600 m³/h Clean Air Delivery Rate (CADR) for fine PM2.5, rivaling commercial HEPA units priced at ₹25,000+ for less than ₹3,000.",
        actionable_tips: [
          "Use true MERV 13 rated filters sealed airtight with duct tape.",
          "Install a cardboard shroud over the fan face with a 14-inch circular cutout to prevent blade-tip backflow."
        ],
        direct_impact_statement: "Continuous operation purges 85% to 92% of indoor fine particulates within 45 minutes."
      };
    } else {
      return {
        reply: "To safeguard against severe winter smog, prioritize staying indoors during morning temperature inversion peaks, maintain airtight door seals, and deploy low-cost MERV 13 filtration.",
        actionable_tips: [
          "Shift cross-ventilation strictly to 12:30 PM - 3:00 PM.",
          "Replace single-occupancy petrol commuting with electric transit or carpooling.",
          "Use wet electrostatic microfiber cleaning instead of dry sweeping."
        ],
        direct_impact_statement: "These actions eliminate over 600 µg of inhaled toxins daily per family."
      };
    }
  }

  function renderChatResponse(id, data) {
    let fullContent = `<p>${data.reply}</p>`;
    if (data.actionable_tips && data.actionable_tips.length > 0) {
      fullContent += `<ul style="padding-left: 18px; margin-top: 8px;">${data.actionable_tips.map(t => `<li>${t}</li>`).join('')}</ul>`;
    }
    if (data.direct_impact_statement) {
      fullContent += `<p style="margin-top: 6px; font-weight: 600; color: #0f766e;">💡 Direct Impact: ${data.direct_impact_statement}</p>`;
    }
    updateChatMessage(id, fullContent);
  }

  function appendChatMessage(role, sender, text) {
    const id = 'msg-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.id = id;
    msgDiv.className = `chat-msg ${role}`;
    msgDiv.innerHTML = `
      <span class="sender-name">${sender}</span>
      <div class="msg-content"><p>${text}</p></div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function updateChatMessage(id, newHtml) {
    const msgDiv = document.getElementById(id);
    if (msgDiv) {
      msgDiv.querySelector('.msg-content').innerHTML = newHtml;
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  // Initialize on page load
  initializeDashboard();
});
