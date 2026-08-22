const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
const labels = { low: "low", medium: "medium", high: "high", critical: "critical" };
const reasonLabels = {
  very_high_amount: "very high amount", high_amount: "high amount", extreme_velocity: "extreme velocity",
  high_velocity: "high velocity", new_device: "new device", new_account: "new account", unusual_hour: "unusual hour"
};

let dashboard;
let activeCity = null;

function renderMetrics(data) {
  document.querySelector("#transactions").textContent = data.summary.transactions.toLocaleString("pt-BR");
  document.querySelector("#volume").textContent = money.format(data.summary.volume_brl).replace("R$", "").trim();
  document.querySelector("#alerts").textContent = data.summary.alerts;
  document.querySelector("#radar-alerts").textContent = data.summary.alerts;
  document.querySelector("#average-risk").textContent = data.summary.average_risk;
}

function renderDistribution(data) {
  const maximum = Math.max(...Object.values(data.risk_distribution));
  document.querySelector("#distribution").innerHTML = Object.entries(data.risk_distribution).map(([level, count]) => `
    <div class="risk-column">
      <strong>${count}</strong>
      <div class="bar" style="height:${Math.max(4, count / maximum * 150)}px"></div>
      <small>${labels[level]}</small>
    </div>`).join("");
}

function renderCities(data) {
  document.querySelector("#cities").innerHTML = data.cities.map(city => `
    <button class="city ${activeCity === city.city ? "active" : ""}" data-city="${city.city}">
      <strong>${city.city}</strong><small>${city.transactions} events · ${city.alerts} alerts</small>
    </button>`).join("");
  document.querySelectorAll(".city").forEach(button => button.addEventListener("click", () => {
    activeCity = button.dataset.city;
    renderCities(data); renderAlerts(data);
  }));
}

function renderReasons(data) {
  const max = Math.max(...data.top_reasons.map(item => item.count));
  document.querySelector("#reasons").innerHTML = data.top_reasons.map(item => `
    <div class="reason-row"><span>${reasonLabels[item.reason] || item.reason}</span>
      <div class="reason-track"><div class="reason-fill" style="width:${item.count / max * 100}%"></div></div><b>${item.count}</b>
    </div>`).join("");
}

function renderAlerts(data) {
  const alerts = activeCity ? data.alerts.filter(item => item.city === activeCity) : data.alerts;
  document.querySelector("#reset-filter").hidden = !activeCity;
  document.querySelector("#alert-rows").innerHTML = alerts.map(item => `
    <tr><td>${item.transaction_id.slice(0, 12)}…</td><td>${item.city}</td><td>${money.format(item.amount_brl)}</td>
    <td><span class="score">${item.risk_score}</span></td><td class="signal">${reasonLabels[item.reasons[0]] || item.reasons[0]}</td></tr>`).join("") ||
    `<tr><td colspan="5">No top alerts for this city in the current sample.</td></tr>`;
}

document.querySelector("#reset-filter").addEventListener("click", () => { activeCity = null; renderCities(dashboard); renderAlerts(dashboard); });

fetch("data/dashboard.json")
  .then(response => { if (!response.ok) throw new Error("dashboard data unavailable"); return response.json(); })
  .then(data => { dashboard = data; renderMetrics(data); renderDistribution(data); renderCities(data); renderReasons(data); renderAlerts(data); })
  .catch(error => { document.querySelector("#alert-rows").innerHTML = `<tr><td colspan="5">${error.message}</td></tr>`; });

