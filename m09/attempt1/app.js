const rosterUrl = "data_room/people/employee_roster.csv";
const headcount = document.querySelector("#headcount");
const headcountOutput = document.querySelector("#headcount-output");
const rosterBody = document.querySelector("#roster-body");
const totalCost = document.querySelector("#total-cost");
const averageCost = document.querySelector("#average-cost");
const rosterShare = document.querySelector("#roster-share");
const costNote = document.querySelector("#cost-note");
const rosterCount = document.querySelector("#roster-count");
const errorMessage = document.querySelector("#error");
let roster = [];

function parseRoster(csv) {
  const lines = csv.split(/\r?\n/).filter((line) => line.trim());
  const headers = lines.shift().split(",");
  return lines.map((line) => {
    const values = line.split(",");
    return headers.reduce((person, header, index) => {
      person[header] = values[index]?.trim() ?? "";
      return person;
    }, {});
  }).filter((person) => person.employee_id && Number.isFinite(Number(person.comp_usd)))
    .sort((a, b) => Number(b.comp_usd) - Number(a.comp_usd));
}

function money(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

function updateScenario() {
  const selectedCount = Number(headcount.value);
  const progress = ((selectedCount - Number(headcount.min)) / (Number(headcount.max) - Number(headcount.min))) * 100;
  const selected = roster.slice(0, selectedCount);
  const total = selected.reduce((sum, person) => sum + Number(person.comp_usd), 0);
  const average = selectedCount ? total / selectedCount : 0;

  headcount.style.setProperty("--fill", `${progress}%`);
  headcountOutput.textContent = `${selectedCount} ${selectedCount === 1 ? "person" : "people"}`;
  totalCost.textContent = money(total);
  averageCost.textContent = money(average);
  rosterShare.textContent = `${Math.round((selectedCount / roster.length) * 100)}%`;
  rosterCount.textContent = `of ${roster.length} people`;
  costNote.textContent = `Top ${selectedCount} by base compensation`;

  rosterBody.innerHTML = selected.map((person, index) => `
    <tr>
      <td class="rank">${String(index + 1).padStart(2, "0")}</td>
      <td><strong>${person.name}</strong><small>${person.employee_id}</small></td>
      <td>${person.role}</td>
      <td><span class="department">${person.department}</span></td>
      <td class="compensation">${money(Number(person.comp_usd))}</td>
    </tr>
  `).join("");
}

async function loadRoster() {
  try {
    const response = await fetch(rosterUrl);
    if (!response.ok) throw new Error(`Roster request returned ${response.status}`);
    roster = parseRoster(await response.text());
    if (!roster.length) throw new Error("No compensated employees found in the roster.");
    headcount.max = roster.length;
    document.querySelector("#max-headcount").textContent = roster.length;
    updateScenario();
  } catch (error) {
    errorMessage.hidden = false;
    errorMessage.textContent = "The roster could not be loaded. Open this app through a local web server so it can read the data room CSV.";
    costNote.textContent = error.message;
  }
}

headcount.addEventListener("input", updateScenario);
loadRoster();