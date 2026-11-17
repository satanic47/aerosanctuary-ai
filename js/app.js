/**
 * AeroSanctuary AI - Interactive Client Application Script
 * Fully asynchronous, accessible, and responsive.
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
      const url = category === 'all' ? '/api/indoor-hacks' : `/api/indoor-hacks?category=${category}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to load IAQ hacks');
      allHacks = await response.json();
      renderIndoorHacks(allHacks);
    } catch (err) {
      console.error(err);
      hacksContainer.innerHTML = `<p class="error-text">Could not load indoor hacks at this moment.</p>`;
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
      const response = await fetch('/api/generate-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Failed to generate action plan');
      const data = await response.json();
      updateDashboard(data);
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend services. Please try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<span>🚀 Generate Tailored Smog Action Plan</span>';
    }
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

      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Chat failed');
      const data = await res.json();

      // Format reply with tips and impact statement
      let fullContent = `<p>${data.reply}</p>`;
      if (data.actionable_tips && data.actionable_tips.length > 0) {
        fullContent += `<ul style="padding-left: 18px; margin-top: 8px;">${data.actionable_tips.map(t => `<li>${t}</li>`).join('')}</ul>`;
      }
      if (data.direct_impact_statement) {
        fullContent += `<p style="margin-top: 6px; font-weight: 600; color: #0f766e;">💡 Direct Impact: ${data.direct_impact_statement}</p>`;
      }

      updateChatMessage(typingId, fullContent);
    } catch (err) {
      console.error(err);
      updateChatMessage(typingId, '<p>Sorry, I encountered an issue retrieving that advice. Please try asking again.</p>');
    }
  });

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
