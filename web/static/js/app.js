// ApproveHub Comprehensive Interactive Logic

let hierarchyData = [];

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Mobile / Web View Toggle
    const toggleBtn = document.getElementById("toggleViewMode");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            document.body.classList.toggle("mobile-mode");
            const isMobile = document.body.classList.contains("mobile-mode");
            toggleBtn.innerHTML = isMobile ? "🖥️ Switch to Web View" : "📱 Switch to App View";
            localStorage.setItem("approvehub_view", isMobile ? "mobile" : "web");
        });
        if (localStorage.getItem("approvehub_view") === "mobile") {
            document.body.classList.add("mobile-mode");
            toggleBtn.innerHTML = "🖥️ Switch to Web View";
        }
    }

    // 2. Fetch Hierarchy Data for Cascading Selectors
    try {
        const resp = await fetch("/api/hierarchy/options");
        if (resp.ok) {
            hierarchyData = await resp.json();
            initCascadingSelectors();
        }
    } catch (e) {
        console.warn("Could not load hierarchy data", e);
    }

    // 3. Initialize Interactive Drag & Drop on Canvas
    initCanvasDragging();
});

// Cascading Approver Dropdowns
function initCascadingSelectors() {
    document.querySelectorAll(".step-card").forEach(card => {
        setupCardDropdowns(card);
    });
}

function setupCardDropdowns(card) {
    const deptSelect = card.querySelector(".dept-select");
    const desigSelect = card.querySelector(".desig-select");
    const nameSelect = card.querySelector(".name-select");

    if (!deptSelect || !desigSelect || !nameSelect) return;

    // Get unique departments
    const departments = [...new Set(hierarchyData.map(a => a.department))];
    const currentDept = deptSelect.value || departments[0];

    // Populate departments if empty
    if (deptSelect.options.length <= 1) {
        deptSelect.innerHTML = "";
        departments.forEach(dept => {
            const opt = document.createElement("option");
            opt.value = dept;
            opt.textContent = dept;
            if (dept === currentDept) opt.selected = true;
            deptSelect.appendChild(opt);
        });
    }

    // Function to populate designations
    function updateDesignations() {
        const selectedDept = deptSelect.value;
        const matchingDesignations = [...new Set(hierarchyData.filter(a => a.department === selectedDept).map(a => a.designation))];
        
        desigSelect.innerHTML = "";
        matchingDesignations.forEach(desig => {
            const opt = document.createElement("option");
            opt.value = desig;
            opt.textContent = desig;
            desigSelect.appendChild(opt);
        });
        updateNames();
    }

    // Function to populate names
    function updateNames() {
        const selectedDept = deptSelect.value;
        const selectedDesig = desigSelect.value;
        const matchingPeople = hierarchyData.filter(a => a.department === selectedDept && a.designation === selectedDesig);

        nameSelect.innerHTML = "";
        matchingPeople.forEach(person => {
            const opt = document.createElement("option");
            opt.value = person.id;
            opt.textContent = `${person.name} (${person.email})`;
            nameSelect.appendChild(opt);
        });

        // Update corresponding label on canvas mark
        const stepNum = card.dataset.step;
        const mark = document.getElementById(`mark_${stepNum}`);
        if (mark && matchingPeople.length > 0) {
            const nameEl = mark.querySelector(".mark-name");
            if (nameEl) nameEl.textContent = matchingPeople[0].name;
        }
    }

    deptSelect.onchange = updateDesignations;
    desigSelect.onchange = updateNames;
    nameSelect.onchange = () => {
        const stepNum = card.dataset.step;
        const mark = document.getElementById(`mark_${stepNum}`);
        if (mark) {
            const selectedText = nameSelect.options[nameSelect.selectedIndex]?.text.split("(")[0].trim();
            const nameEl = mark.querySelector(".mark-name");
            if (nameEl) nameEl.textContent = selectedText;
        }
    };

    updateDesignations();
}

// Dynamic Add & Remove Approver Tiers
let stepCounter = 2;

function addApproverTier() {
    stepCounter++;
    const container = document.getElementById("approverList");
    const canvas = document.getElementById("a4Canvas");
    if (!container || !canvas) return;

    const newStepDiv = document.createElement("div");
    newStepDiv.className = "step-card";
    newStepDiv.dataset.step = stepCounter;
    newStepDiv.style.cssText = "background:var(--bg);border:1px solid var(--bd);border-radius:12px;padding:14px;position:relative;";
    
    newStepDiv.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-weight:700;font-size:12.5px;color:var(--vio);">Step ${stepCounter}: Additional Authority</span>
            <div style="display:flex;gap:6px;align-items:center;">
                <span class="pill waiting">Waiting</span>
                <button type="button" class="btn secondary" onclick="removeApproverTier(${stepCounter})" style="padding:2px 8px;font-size:11px;color:var(--er);">✕</button>
            </div>
        </div>
        <div class="form-group" style="margin-bottom:8px;">
            <label style="font-size:11px;">1. Branch / Department</label>
            <select class="dept-select" style="font-size:12px;padding:6px;"></select>
        </div>
        <div class="form-group" style="margin-bottom:8px;">
            <label style="font-size:11px;">2. Designation / Post</label>
            <select class="desig-select" style="font-size:12px;padding:6px;"></select>
        </div>
        <div class="form-group" style="margin-bottom:8px;">
            <label style="font-size:11px;">3. Authorized Person</label>
            <select class="name-select approver-select" style="font-size:12px;padding:6px;"></select>
        </div>
        <div style="display:flex;gap:12px;font-size:11px;margin-top:4px;">
            <label><input type="radio" name="mark_type_${stepCounter}" value="signature" checked> Signature</label>
            <label><input type="radio" name="mark_type_${stepCounter}" value="stamp"> Stamp</label>
            <label><input type="radio" name="mark_type_${stepCounter}" value="seal"> Seal</label>
        </div>
    `;
    container.appendChild(newStepDiv);
    setupCardDropdowns(newStepDiv);

    // Create corresponding mark on A4 canvas
    const newMark = document.createElement("div");
    newMark.className = "stamp-mark";
    newMark.id = `mark_${stepCounter}`;
    newMark.dataset.step = stepCounter;
    
    const topOffset = Math.min(500, 360 + (stepCounter - 1) * 45);
    newMark.style.cssText = `left:35px;top:${topOffset}px;border-color:var(--vio);`;
    newMark.dataset.posX = "0.08";
    newMark.dataset.posY = (topOffset / 640).toFixed(4);

    newMark.innerHTML = `
        <div class="badge-icon" style="background:var(--vio);">✓</div>
        <div style="text-align:left;line-height:1.2;">
            <b style="font-size:10.5px;color:var(--vio);">Step ${stepCounter} Mark</b>
            <div class="mark-name" style="font-size:9.5px;color:var(--mu);">Authority</div>
            <div style="font-size:8px;color:#888;">Drag to position</div>
        </div>
    `;
    canvas.appendChild(newMark);
    attachDragHandler(newMark, canvas);
}

function removeApproverTier(stepNum) {
    const card = document.querySelector(`.step-card[data-step="${stepNum}"]`);
    const mark = document.getElementById(`mark_${stepNum}`);
    if (card) card.remove();
    if (mark) mark.remove();
}

// Interactive Canvas Dragging for Marks and QR Code
function initCanvasDragging() {
    const canvas = document.getElementById("a4Canvas");
    if (!canvas) return;

    document.querySelectorAll(".stamp-mark, .qr-stamp-mark").forEach(el => {
        attachDragHandler(el, canvas);
    });
}

function attachDragHandler(el, canvas) {
    let active = false;
    let startX = 0, startY = 0;
    let initialLeft = 0, initialTop = 0;

    el.addEventListener("pointerdown", (e) => {
        active = true;
        el.setPointerCapture(e.pointerId);
        const rect = el.getBoundingClientRect();
        const parentRect = canvas.getBoundingClientRect();

        startX = e.clientX;
        startY = e.clientY;
        initialLeft = rect.left - parentRect.left;
        initialTop = rect.top - parentRect.top;
        e.preventDefault();
    });

    el.addEventListener("pointermove", (e) => {
        if (!active) return;
        const parentRect = canvas.getBoundingClientRect();
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;

        let newX = initialLeft + deltaX;
        let newY = initialTop + deltaY;

        const maxX = parentRect.width - el.offsetWidth - 8;
        const maxY = parentRect.height - el.offsetHeight - 8;
        newX = Math.max(8, Math.min(newX, maxX));
        newY = Math.max(8, Math.min(newY, maxY));

        // 5% snap
        const snapX = parentRect.width * 0.05;
        const snapY = parentRect.height * 0.05;
        newX = Math.round(newX / snapX) * snapX;
        newY = Math.round(newY / snapY) * snapY;

        el.style.left = `${newX}px`;
        el.style.top = `${newY}px`;

        el.dataset.posX = (newX / parentRect.width).toFixed(4);
        el.dataset.posY = (newY / parentRect.height).toFixed(4);
    });

    el.addEventListener("pointerup", (e) => {
        if (active) {
            el.releasePointerCapture(e.pointerId);
            active = false;
        }
    });
}

// PIN Keypad Management
let currentPin = "";
let currentStepActionId = null;

function openPinModal(stepId) {
    currentPin = "";
    currentStepActionId = stepId;
    updatePinDots();
    const modal = document.getElementById("pinModal");
    if (modal) modal.classList.add("active");
}

function closePinModal() {
    currentPin = "";
    currentStepActionId = null;
    const modal = document.getElementById("pinModal");
    if (modal) modal.classList.remove("active");
}

function pressKey(digit) {
    if (currentPin.length < 6) {
        currentPin += digit;
        updatePinDots();
        if (currentPin.length === 4) {
            submitApprovalWithPin();
        }
    }
}

function backspaceKey() {
    if (currentPin.length > 0) {
        currentPin = currentPin.slice(0, -1);
        updatePinDots();
    }
}

function updatePinDots() {
    const dots = document.querySelectorAll(".pin-dot");
    dots.forEach((dot, index) => {
        if (index < currentPin.length) {
            dot.classList.add("filled");
        } else {
            dot.classList.remove("filled");
        }
    });
}

async function submitApprovalWithPin() {
    if (!currentStepActionId) return;
    const errorEl = document.getElementById("pinError");
    if (errorEl) errorEl.textContent = "Verifying PIN and stamping official document...";

    try {
        const resp = await fetch(`/api/steps/${currentStepActionId}/action`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                action: "approve",
                pin: currentPin,
                remark: "Approved with security PIN verification."
            })
        });

        const data = await resp.json();
        if (resp.ok && data.success) {
            closePinModal();
            window.location.reload();
        } else {
            if (errorEl) errorEl.textContent = data.error || "Incorrect PIN.";
            currentPin = "";
            updatePinDots();
        }
    } catch (err) {
        if (errorEl) errorEl.textContent = "Network error. Try again.";
    }
}
