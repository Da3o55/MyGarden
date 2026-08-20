// ---------- Navigation ----------
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");

        if (btn.dataset.tab === "list") loadAllPlants();
        if (btn.dataset.tab === "today") loadToday();
    });
});

// ---------- Remplissage des selects mois ----------
const MONTHS = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

function fillMonthSelects() {
    const selects = document.querySelectorAll("select[id$='_month']");
    selects.forEach(sel => {
        sel.innerHTML = '<option value="">--</option>';
        for (let i = 1; i <= 12; i++) {
            const opt = document.createElement("option");
            opt.value = i;
            opt.textContent = MONTHS[i];
            sel.appendChild(opt);
        }
    });
}
fillMonthSelects();

// ---------- Rendu d'une carte plante ----------
function renderPlantCard(p, editable = false) {
    const div = document.createElement("div");
    div.className = "plant-card";

    const img = p.image_url
        ? `<img src="${p.image_url}" alt="${p.common_name}">`
        : `<img src="https://via.placeholder.com/300x150/e0e0e0/999?text=🌿" alt="">`;

    div.innerHTML = `
        ${img}
        <h4>${p.common_name}</h4>
        <div class="scientific">${p.scientific_name || ""}</div>
        <div class="info-line">☀️ ${p.exposure || "-"}</div>
        <div class="info-line">🌱 ${p.plant_type || "-"}</div>
        <div class="info-line">💧 ${p.soil_humidity || "-"}</div>
        <div class="info-line">📏 ${p.height || "-"}</div>
        ${editable ? `
        <div class="card-actions">
            <button class="btn-edit" onclick="editPlant(${p.id})">✏️ Modifier</button>
            <button class="btn-delete" onclick="deletePlant(${p.id})">🗑️ Supprimer</button>
        </div>` : ""}
    `;
    return div;
}

// ---------- Onglet Aujourd'hui ----------
async function loadToday() {
    const res = await fetch("api/today");
    const data = await res.json();

    document.getElementById("today-date").textContent =
        `📅 ${data.date} — ${data.month_name}`;

    fillSection("blooming-list", data.blooming, "Aucune plante en floraison ce mois-ci.");
    fillSection("pruning-list", data.pruning, "Aucune taille à prévoir ce mois-ci.");
    fillSection("fertilizing-list", data.fertilizing, "Aucun engrais à prévoir ce mois-ci.");
}

function fillSection(elementId, plants, emptyMsg) {
    const container = document.getElementById(elementId);
    container.innerHTML = "";
    if (plants.length === 0) {
        container.innerHTML = `<div class="empty-msg">${emptyMsg}</div>`;
        return;
    }
    plants.forEach(p => container.appendChild(renderPlantCard(p, false)));
}

// ---------- Onglet Liste ----------
async function loadAllPlants() {
    const res = await fetch("api/plants");
    const plants = await res.json();

    const container = document.getElementById("all-plants-list");
    container.innerHTML = "";
    if (plants.length === 0) {
        container.innerHTML = `<div class="empty-msg">Aucune plante enregistrée.</div>`;
        return;
    }
    plants.forEach(p => container.appendChild(renderPlantCard(p, true)));
}

// ---------- Ajout / Modification ----------
const form = document.getElementById("plant-form");
const cancelBtn = document.getElementById("cancel-edit");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("f-id").value;
    const payload = {
        common_name: document.getElementById("f-common_name").value,
        scientific_name: document.getElementById("f-scientific_name").value,
        exposure: document.getElementById("f-exposure").value,
        soil_type: document.getElementById("f-soil_type").value,
        plant_type: document.getElementById("f-plant_type").value,
        hardiness: document.getElementById("f-hardiness").value,
        soil_humidity: document.getElementById("f-soil_humidity").value,
        foliage_type: document.getElementById("f-foliage_type").value,
        height: document.getElementById("f-height").value,
        bloom_start_month: parseInt(document.getElementById("f-bloom_start_month").value) || null,
        bloom_end_month: parseInt(document.getElementById("f-bloom_end_month").value) || null,
        known_diseases: document.getElementById("f-known_diseases").value,
        pruning_start_month: parseInt(document.getElementById("f-pruning_start_month").value) || null,
        pruning_end_month: parseInt(document.getElementById("f-pruning_end_month").value) || null,
        pruning_advice: document.getElementById("f-pruning_advice").value,
        fertilize_start_month: parseInt(document.getElementById("f-fertilize_start_month").value) || null,
        fertilize_end_month: parseInt(document.getElementById("f-fertilize_end_month").value) || null,
        fertilize_quantity: document.getElementById("f-fertilize_quantity").value,
        fertilize_type: document.getElementById("f-fertilize_type").value,
        image_url: document.getElementById("f-image_url").value,
        notes: document.getElementById("f-notes").value
    };

    const url = id ? `/api/plants/${id}` : "/api/plants";
    const method = id ? "PUT" : "POST";

    const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        alert(id ? "✅ Plante mise à jour !" : "✅ Plante ajoutée !");
        resetForm();
        document.querySelector('[data-tab="list"]').click();
    } else {
        alert("❌ Erreur lors de l'enregistrement");
    }
});

cancelBtn.addEventListener("click", resetForm);

function resetForm() {
    form.reset();
    document.getElementById("f-id").value = "";
    cancelBtn.style.display = "none";
}

async function editPlant(id) {
    const res = await fetch(`api/plants/${id}`);
    const p = await res.json();

    document.getElementById("f-id").value = p.id;
    document.getElementById("f-common_name").value = p.common_name || "";
    document.getElementById("f-scientific_name").value = p.scientific_name || "";
    document.getElementById("f-exposure").value = p.exposure || "";
    document.getElementById("f-soil_type").value = p.soil_type || "";
    document.getElementById("f-plant_type").value = p.plant_type || "Fleur";
    document.getElementById("f-hardiness").value = p.hardiness || "";
    document.getElementById("f-soil_humidity").value = p.soil_humidity || "";
    document.getElementById("f-foliage_type").value = p.foliage_type || "Caduc";
    document.getElementById("f-height").value = p.height || "";
    document.getElementById("f-bloom_start_month").value = p.bloom_start_month || "";
    document.getElementById("f-bloom_end_month").value = p.bloom_end_month || "";
    document.getElementById("f-known_diseases").value = p.known_diseases || "";
    document.getElementById("f-pruning_start_month").value = p.pruning_start_month || "";
    document.getElementById("f-pruning_end_month").value = p.pruning_end_month || "";
    document.getElementById("f-pruning_advice").value = p.pruning_advice || "";
    document.getElementById("f-fertilize_start_month").value = p.fertilize_start_month || "";
    document.getElementById("f-fertilize_end_month").value = p.fertilize_end_month || "";
    document.getElementById("f-fertilize_quantity").value = p.fertilize_quantity || "";
    document.getElementById("f-fertilize_type").value = p.fertilize_type || "";
    document.getElementById("f-image_url").value = p.image_url || "";
    document.getElementById("f-notes").value = p.notes || "";

    cancelBtn.style.display = "inline-block";
    document.querySelector('[data-tab="add"]').click();
}

async function deletePlant(id) {
    if (!confirm("Supprimer cette plante ?")) return;
    const res = await fetch(`api/plants/${id}`, { method: "DELETE" });
    if (res.ok) {
        alert("✅ Plante supprimée");
        loadAllPlants();
    }
}

// ---------- Recherche externe (Perenual) ----------
document.getElementById("external-search-btn").addEventListener("click", async () => {
    const query = document.getElementById("external-search-input").value.trim();
    if (!query) return;

    const resultsDiv = document.getElementById("external-results");
    resultsDiv.innerHTML = "<p>Recherche en cours...</p>";

    const res = await fetch(`api/external-search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    resultsDiv.innerHTML = "";

    if (data.error) {
        resultsDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
        return;
    }

    if (data.results.length === 0) {
        resultsDiv.innerHTML = "<p>Aucun résultat.</p>";
        return;
    }

    data.results.forEach(item => {
        const div = document.createElement("div");
        div.className = "external-result-card";
        const img = item.image_url
            ? `<img src="${item.image_url}" alt="">`
            : `<img src="https://via.placeholder.com/150x80/e0e0e0/999?text=🌿" alt="">`;
        div.innerHTML = `
            ${img}
            <strong>${item.common_name || "?"}</strong>
            <div style="font-style:italic;font-size:11px;">${item.scientific_name || ""}</div>
        `;
        div.addEventListener("click", () => fillFormFromExternal(item.external_id));
        resultsDiv.appendChild(div);
    });
});

async function fillFormFromExternal(externalId) {
    const res = await fetch(`api/external-detail/${externalId}`);
    const data = await res.json();

    if (data.error) {
        alert("Erreur: " + data.error);
        return;
    }

    document.getElementById("f-common_name").value = data.common_name || "";
    document.getElementById("f-scientific_name").value = data.scientific_name || "";
    document.getElementById("f-exposure").value = data.exposure || "";
    document.getElementById("f-plant_type").value = data.plant_type || "Fleur";
    document.getElementById("f-hardiness").value = data.hardiness || "";
    document.getElementById("f-soil_humidity").value = data.soil_humidity || "";
    document.getElementById("f-foliage_type").value = data.foliage_type || "Caduc";
    document.getElementById("f-image_url").value = data.image_url || "";

    alert("✅ Champs pré-remplis ! Complétez le reste puis enregistrez.");
    window.scrollTo({ top: document.getElementById("plant-form").offsetTop, behavior: "smooth" });
}

// ---------- Chargement initial ----------
loadToday();