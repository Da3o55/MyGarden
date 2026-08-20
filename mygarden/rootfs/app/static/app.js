// ---------- Navigation ----------
document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`view-${btn.dataset.view}`).classList.add("active");

        if (btn.dataset.view === "list") loadPlantsList();
        if (btn.dataset.view === "calendar") loadCalendar();
    });
});

// ---------- Calendrier ----------
async function loadCalendar() {
    const dateEl = document.getElementById("today-date");
    dateEl.textContent = new Date().toLocaleDateString("fr-FR", {
        weekday: "long", year: "numeric", month: "long", day: "numeric"
    });

    const content = document.getElementById("calendar-content");
    content.innerHTML = "<div class='loading'>Chargement...</div>";

    try {
        const res = await fetch("/api/calendar/today");
        const data = await res.json();

        let html = "";

        html += renderCalendarSection("🌸 En floraison", data.flowering, item =>
            `<div class="detail">Actuellement en fleurs</div>`
        );

        html += renderCalendarSection("✂️ À tailler", data.pruning, item =>
            `<div class="detail">${item.advice || "Voir fiche plante"}</div>`
        );

        html += renderCalendarSection("🌿 À fertiliser", data.fertilizing, item =>
            `<div class="detail">${item.type || ""} - ${item.quantity || ""}</div>`
        );

        if (!html) {
            html = "<div class='empty-state'>🌤️ Aucune action prévue aujourd'hui</div>";
        }

        content.innerHTML = html;
    } catch (e) {
        content.innerHTML = "<div class='empty-state'>Erreur de chargement</div>";
    }
}

function renderCalendarSection(title, items, detailFn) {
    if (!items || items.length === 0) return "";

    let html = `<div class="calendar-section"><h3>${title}</h3>`;
    items.forEach(item => {
        html += `
            <div class="calendar-item">
                <img src="${item.image_url || 'https://via.placeholder.com/50'}" onerror="this.src='https://via.placeholder.com/50'">
                <div class="info">
                    <strong>${item.common_name}</strong>
                    <em>${item.scientific_name || ""}</em>
                    ${detailFn(item)}
                </div>
            </div>
        `;
    });
    html += "</div>";
    return html;
}

// ---------- Liste des plantes ----------
async function loadPlantsList(search = "") {
    const container = document.getElementById("plants-list");
    container.innerHTML = "<div class='loading'>Chargement...</div>";

    try {
        const url = search ? `/api/plants?search=${encodeURIComponent(search)}` : "/api/plants";
        const res = await fetch(url);
        const plants = await res.json();

        if (plants.length === 0) {
            container.innerHTML = "<div class='empty-state'>Aucune plante trouvée</div>";
            return;
        }

        container.innerHTML = plants.map(p => `
            <div class="plant-card" onclick="showPlantDetail(${p.id})">
                <img src="${p.image_url || 'https://via.placeholder.com/200x120'}" onerror="this.src='https://via.placeholder.com/200x120'">
                <h4>${p.common_name}</h4>
                <em>${p.scientific_name || ""}</em>
                <div class="tags">
                    ${p.plant_type ? `<span class="tag">${p.plant_type}</span>` : ""}
                    ${p.exposure ? `<span class="tag">${p.exposure}</span>` : ""}
                </div>
            </div>
        `).join("");
    } catch (e) {
        container.innerHTML = "<div class='empty-state'>Erreur de chargement</div>";
    }
}

document.getElementById("search-input").addEventListener("input", (e) => {
    loadPlantsList(e.target.value);
});

// ---------- Détail plante (modal) ----------
async function showPlantDetail(id) {
    const res = await fetch(`/api/plants/${id}`);
    const p = await res.json();

    const modal = document.getElementById("plant-modal");
    const body = document.getElementById("modal-body");

    body.innerHTML = `
        <h2>${p.common_name}</h2>
        <em>${p.scientific_name || ""}</em>
        <img src="${p.image_url || 'https://via.placeholder.com/400x200'}" style="width:100%;border-radius:8px;margin:15px 0;" onerror="this.src='https://via.placeholder.com/400x200'">

        ${detailRow("Exposition", p.exposure)}
        ${detailRow("Type de sol", p.soil_type)}
        ${detailRow("Type de plante", p.plant_type)}
        ${detailRow("Rusticité", p.hardiness)}
        ${detailRow("Humidité du sol", p.soil_humidity)}
        ${detailRow("Feuillage", p.foliage_type)}
        ${detailRow("Hauteur", (p.height_min && p.height_max) ? `${p.height_min}m - ${p.height_max}m` : "")}
        ${detailRow("Floraison", (p.flowering_start && p.flowering_end) ? `${p.flowering_start} au ${p.flowering_end}` : "")}
        ${detailRow("Maladies connues", p.known_diseases)}
        ${detailRow("Période de taille", (p.pruning_start && p.pruning_end) ? `${p.pruning_start} au ${p.pruning_end}` : "")}
        ${detailRow("Conseils de taille", p.pruning_advice)}
        ${detailRow("Période engrais", (p.fertilizing_start && p.fertilizing_end) ? `${p.fertilizing_start} au ${p.fertilizing_end}` : "")}
        ${detailRow("Quantité engrais", p.fertilizing_quantity)}
        ${detailRow("Type engrais", p.fertilizing_type)}
        ${detailRow("Emplacement", p.garden_location)}
        ${detailRow("Date de plantation", p.date_planted)}
        ${detailRow("Notes", p.notes)}

        <div style="margin-top:20px;display:flex;gap:10px;">
            <button class="btn-primary" onclick="editPlant(${p.id})">✏️ Modifier</button>
            <button class="btn-primary" style="background:#c0392b" onclick="deletePlant(${p.id})">🗑️ Supprimer</button>
        </div>
    `;

    modal.classList.remove("hidden");
}

function detailRow(label, value) {
    if (!value) return "";
    return `<div class="detail-row"><strong>${label}</strong><span>${value}</span></div>`;
}

document.querySelector(".close-modal").addEventListener("click", () => {
    document.getElementById("plant-modal").classList.add("hidden");
});

async function