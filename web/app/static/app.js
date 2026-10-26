let ws = null;
let reconnectTimer = null;
let autoScroll = true;
let userScrolledUp = false;

// Active tracking
let currentDocketId = null;
let currentPhaseIndex = null;
let activeSpeechCard = null;
let activeSpeechBody = null;
let activeCursor = null;

// DOM Elements
const observersCountEl = document.getElementById("observers-count");
const courtSessionTextEl = document.getElementById("court-session-text");
const currentRangeEl = document.getElementById("current-range");
const activeDocketBadgeEl = document.getElementById("active-docket-badge");
const readingStatusTextEl = document.getElementById("reading-status-text");
const recessCardEl = document.getElementById("recess-card");
const recessCounterEl = document.getElementById("recess-counter");
const courtroomFeedEl = document.getElementById("courtroom-feed");
const jumpLatestBtnEl = document.getElementById("jump-latest-btn");
const queueStatusPillEl = document.getElementById("queue-status-pill");
const queueInfoTextEl = document.getElementById("queue-info-text");
const payloadInputEl = document.getElementById("payload-input");
const submitBtnEl = document.getElementById("submit-btn");
const boundsHintEl = document.getElementById("bounds-hint");
const inputFeedbackEl = document.getElementById("input-feedback");
const ledgerListEl = document.getElementById("ledger-list");
const ledgerCountEl = document.getElementById("ledger-count");
const standbyOverlayEl = document.getElementById("standby-overlay");
const caseModalEl = document.getElementById("case-modal");
const modalCaseTitleEl = document.getElementById("modal-case-title");
const modalCaseMetaEl = document.getElementById("modal-case-meta");
const modalCaseBodyEl = document.getElementById("modal-case-body");

const AVATARS = {
    bailiff: "🛡️",
    judge: "👨‍⚖️",
    historian: "📜",
    fizz: "🔵",
    buzz: "🟠",
    auditor: "🔬",
    regulator: "⚖️",
    appellate: "🏛️",
    orator: "🎙️",
    clerk: "🏛️"
};

// Connect WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("Connected to Byzantine Courtroom WebSocket.");
        courtSessionTextEl.innerText = "COURT IN SESSION";
        courtSessionTextEl.style.color = "var(--color-auditor)";
        sendVisibilityHeartbeat();
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleServerEvent(data);
        } catch (e) {
            console.error("Failed to parse websocket event:", e);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 2s...");
        courtSessionTextEl.innerText = "RECONNECTING...";
        courtSessionTextEl.style.color = "var(--color-buzz)";
        clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        ws.close();
    };
}

function sendVisibilityHeartbeat() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const isVisible = document.visibilityState === "visible";
        ws.send(JSON.stringify({
            type: "VISIBILITY_HEARTBEAT",
            active: isVisible
        }));
    }
}

document.addEventListener("visibilitychange", sendVisibilityHeartbeat);

setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "HEARTBEAT" }));
    }
}, 5000);

// Detect User Scroll in the Feed
courtroomFeedEl.addEventListener("scroll", () => {
    const distanceToBottom = courtroomFeedEl.scrollHeight - courtroomFeedEl.scrollTop - courtroomFeedEl.clientHeight;
    if (distanceToBottom > 80) {
        userScrolledUp = true;
        jumpLatestBtnEl.classList.remove("hidden");
    } else {
        userScrolledUp = false;
        jumpLatestBtnEl.classList.add("hidden");
    }
});

function toggleAutoScroll(enabled) {
    autoScroll = enabled;
    if (enabled) {
        scrollToBottom(true);
    }
}

function scrollToBottom(force = false) {
    if (force || (autoScroll && !userScrolledUp)) {
        courtroomFeedEl.scrollTop = courtroomFeedEl.scrollHeight;
        if (force) {
            userScrolledUp = false;
            jumpLatestBtnEl.classList.add("hidden");
        }
    }
}

function clearFeedVisuals() {
    courtroomFeedEl.innerHTML = `
        <div class="feed-welcome-banner">
            <div class="welcome-icon">🏛️</div>
            <h3>Feed Display Cleared</h3>
            <p>New proceedings will appear below. Historical database records remain permanently saved.</p>
        </div>
    `;
    activeSpeechCard = null;
    activeSpeechBody = null;
    activeCursor = null;
}

// Event Dispatcher
function handleServerEvent(data) {
    switch (data.event) {
        case "INITIAL_STATE":
            observersCountEl.innerText = data.active_observers || 1;
            updateQueueStatus(data.scheduler);
            renderLedger(data.history || []);
            break;

        case "STANDBY_CHANGE":
            if (data.is_standby) {
                courtSessionTextEl.innerText = "STANDBY (SLEEP)";
                courtSessionTextEl.style.color = "var(--color-buzz)";
                if (readingStatusTextEl) readingStatusTextEl.innerText = "Standby sleep: 0 active observers (saving compute).";
                standbyOverlayEl.classList.remove("hidden");
            } else {
                courtSessionTextEl.innerText = "COURT IN SESSION";
                courtSessionTextEl.style.color = "var(--color-auditor)";
                standbyOverlayEl.classList.add("hidden");
            }
            break;

        case "RECESS_TICK":
            finalizeActiveSpeech();
            recessCardEl.classList.remove("hidden");
            recessCounterEl.innerText = data.seconds_remaining;
            updateQueueStatus(data.queue_status);
            courtSessionTextEl.innerText = `RECESS (${data.seconds_remaining}s)`;
            courtSessionTextEl.style.color = "var(--color-appellate)";
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Parliamentary Recess: ${data.seconds_remaining}s until next docket. Submit queued number on right!`;
            break;

        case "QUEUE_UPDATED":
            updateQueueStatus(data.queue_status);
            break;

        case "RANGE_EXPANDED":
            currentRangeEl.innerText = `${data.old_end + 1}..${data.new_end}`;
            break;

        case "DOCKET_START":
            finalizeActiveSpeech();
            const welcomeStart = document.getElementById("feed-welcome");
            if (welcomeStart) welcomeStart.remove();
            recessCardEl.classList.add("hidden");
            currentDocketId = data.docket_id;
            if (activeDocketBadgeEl) activeDocketBadgeEl.innerText = `Docket: ${data.docket_id} (Payload '${data.payload}')`;
            courtSessionTextEl.innerText = `ADJUDICATING: ${data.docket_id} ('${data.payload}')`;
            courtSessionTextEl.style.color = "var(--color-auditor)";
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Convening on Docket ${data.docket_id} (Payload '${data.payload}')...`;
            resetPhaseTimeline();

            // Insert Docket Divider into continuous feed
            appendDocketDivider(data.docket_id, data.payload, data.source, data.digital_root, data.terminal_glyph);
            scrollToBottom();
            break;

        case "PHASE_TRANSITION":
        case "STAGE_TRANSITION":
            finalizeActiveSpeech();
            const phaseIndex = data.phase_index !== undefined ? data.phase_index : data.stage_index;
            const phaseName = data.phase_name || data.stage_name;
            setPhaseActive(phaseIndex);
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Hearing ${phaseName} • ${data.speaker}`;

            // Create new persistent speech card in feed
            createSpeechCard(phaseName, data.speaker, data.speaker_role);
            scrollToBottom();
            break;

        case "TOKEN_STREAM":
            if (activeSpeechBody) {
                activeSpeechBody.innerText += data.token;
                scrollToBottom();
            }
            break;

        case "SPEECH_COMPLETE":
            if (activeSpeechBody && data.full_text) {
                activeSpeechBody.innerHTML = formatInlineMarkdown(data.full_text);
                if (data.action && activeSpeechCard) {
                    const header = activeSpeechCard.querySelector(".speech-card-header");
                    if (header && !header.querySelector(".speech-action-tag")) {
                        const actionTag = document.createElement("span");
                        actionTag.className = `speech-action-tag action-${data.action.replace(/_/g, '-')}`;
                        actionTag.innerText = `Action: ${data.action.replace(/_/g, ' ')}`;
                        header.insertBefore(actionTag, header.querySelector(".speech-status-tag"));
                    }
                }
                scrollToBottom();
            }
            break;

        case "DOCKET_CONCLUDED":
            finalizeActiveSpeech();
            appendVerdictCard(data.docket_id, data.payload, data.final_token, data.verdict);
            if (readingStatusTextEl) readingStatusTextEl.innerText = `Docket ${data.docket_id} concluded with emission '${data.final_token}'. Entering recess.`;
            fetchRecentHistory();
            if (typeof rotateAmazonAds === "function") rotateAmazonAds();
            scrollToBottom();
            break;
    }
}

function setPhaseActive(phaseIndex) {
    currentPhaseIndex = phaseIndex;
    const steps = document.querySelectorAll(".phase-step, .stage-step");
    if (!steps || steps.length === 0) return;
    steps.forEach((step, idx) => {
        step.classList.remove("active");
        if (idx < phaseIndex) {
            step.classList.add("completed");
        } else if (idx === phaseIndex) {
            step.classList.add("active");
        } else {
            step.classList.remove("completed");
        }
    });
}

function resetPhaseTimeline() {
    const steps = document.querySelectorAll(".phase-step, .stage-step");
    if (!steps || steps.length === 0) return;
    steps.forEach(step => {
        step.classList.remove("active", "completed");
    });
}

// Feed Element Generators (Text is NEVER removed)
function appendDocketDivider(docketId, payload, source, root, glyph) {
    const divider = document.createElement("div");
    divider.className = "docket-divider";
    divider.innerHTML = `
        <div class="docket-divider-kicker">🔔 NEW INQUISITION DOCKET CONVENED</div>
        <div class="docket-divider-main">
            <div class="docket-divider-left">
                <span class="docket-badge-title">⚖️ ${escapeHtml(docketId)}</span>
                <span class="docket-payload-pill">PAYLOAD '${escapeHtml(payload)}'</span>
                <span class="docket-badge-source">${escapeHtml(source)}</span>
            </div>
            <div class="docket-divider-right">
                <span class="docket-meta-chip">Digital Root: <strong>${escapeHtml(root)}</strong></span>
                <span class="docket-meta-chip">Terminal Glyph: <strong>'${escapeHtml(glyph)}'</strong></span>
            </div>
        </div>
    `;
    courtroomFeedEl.appendChild(divider);
}

function formatInlineMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italics: *text* or _text_
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    return html;
}

function createSpeechCard(phaseTitle, speaker, role) {
    const welcome = document.getElementById("feed-welcome");
    if (welcome) welcome.remove();

    const card = document.createElement("div");
    card.className = `speech-card ${role} active`;

    const avatar = AVATARS[role] || "🏛️";
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    card.innerHTML = `
        <div class="speech-card-header">
            <div class="speech-speaker-info">
                <span class="speech-avatar">${avatar}</span>
                <span class="speech-speaker-name">${escapeHtml(speaker)}</span>
            </div>
            <span class="speech-status-tag" id="status-tag">Speaking... • ${now}</span>
        </div>
        <div class="speech-card-body"><span class="speech-text"></span><span class="speech-cursor">▋</span></div>
    `;

    courtroomFeedEl.appendChild(card);
    activeSpeechCard = card;
    activeSpeechBody = card.querySelector(".speech-text");
    activeCursor = card.querySelector(".speech-cursor");
}

function finalizeActiveSpeech() {
    if (activeSpeechCard) {
        activeSpeechCard.classList.remove("active");
        if (activeCursor) {
            activeCursor.remove();
            activeCursor = null;
        }
        const statusTag = activeSpeechCard.querySelector("#status-tag");
        if (statusTag) {
            statusTag.innerText = "Admitted into Record";
        }
        if (activeSpeechBody) {
            const raw = activeSpeechBody.innerText.trim();
            if (!raw) {
                activeSpeechBody.innerHTML = "<em>[Testimony recorded in official ledger.]</em>";
            } else {
                activeSpeechBody.innerHTML = formatInlineMarkdown(raw);
            }
        }
        activeSpeechCard = null;
        activeSpeechBody = null;
    }
}

function appendVerdictCard(docketId, payload, token, verdict) {
    const card = document.createElement("div");
    card.className = "docket-verdict-card";
    card.innerHTML = `
        <div class="verdict-card-label">CERTIFIED BYZANTINE CONSENSUS EMISSION • ${escapeHtml(docketId)} (PAYLOAD '${escapeHtml(payload)}')</div>
        <div class="verdict-card-token">${escapeHtml(token)}</div>
        <div class="verdict-card-desc">${escapeHtml(verdict)}</div>
    `;
    courtroomFeedEl.appendChild(card);
}

// Queue Management
function toggleQueueHelp() {
    const popover = document.getElementById("queue-help-popover");
    const btn = document.getElementById("queue-help-btn");
    if (!popover) return;
    const isHidden = popover.classList.toggle("hidden");
    if (btn) {
        btn.classList.toggle("active", !isHidden);
    }
}

function updateQueueStatus(status) {
    if (!status) return;
    if (currentRangeEl) currentRangeEl.innerText = `${status.range_start}..${status.range_end}`;
    if (boundsHintEl) boundsHintEl.innerText = `Allowed range: ${status.min_allowed} to ${status.max_allowed}`;

    if (status.is_queue_full && status.queued_docket) {
        queueStatusPillEl.innerText = "Occupied";
        queueStatusPillEl.className = "queue-status-indicator occupied";
        if (queueInfoTextEl) {
            queueInfoTextEl.innerHTML = `<strong>Locked:</strong> Payload <code>'${escapeHtml(status.queued_docket.payload)}'</code> is queued for the immediate next docket!`;
        }
        payloadInputEl.disabled = true;
        submitBtnEl.disabled = true;
    } else {
        queueStatusPillEl.innerText = "Ready";
        queueStatusPillEl.className = "queue-status-indicator";
        if (queueInfoTextEl) {
            queueInfoTextEl.innerText = "The priority queue is empty. Submit a number now to claim the upcoming docket!";
        }
        payloadInputEl.disabled = false;
        submitBtnEl.disabled = false;
    }
}

function validateInput(el) {
    el.value = el.value.replace(/[^0-9]/g, "");
    if (el.value.length > 100) {
        el.value = el.value.slice(0, 100);
    }
}

async function submitQueue(e) {
    e.preventDefault();
    const rawVal = payloadInputEl.value.trim();
    if (!rawVal) return;

    inputFeedbackEl.className = "input-feedback hidden";

    try {
        const res = await fetch("/api/queue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ payload: rawVal })
        });
        const data = await res.json();
        if (res.ok) {
            inputFeedbackEl.innerText = data.message;
            inputFeedbackEl.className = "input-feedback success";
            payloadInputEl.value = "";
            updateQueueStatus(data.status);
        } else {
            inputFeedbackEl.innerText = data.detail || "Submission rejected.";
            inputFeedbackEl.className = "input-feedback error";
        }
    } catch (err) {
        inputFeedbackEl.innerText = "Network error communicating with tribunal.";
        inputFeedbackEl.className = "input-feedback error";
    }
}

// Historical Records & Modal
let allArchivesDockets = [];
let filteredArchivesDockets = [];
let archivesOrder = "desc"; // Default: Order of Inquisition (Latest -> 1st, matching Historical Precedents)
let archivesFilter = "all";
let selectedArchivesCaseId = null;

async function fetchRecentHistory() {
    try {
        const res = await fetch("/api/history?limit=30");
        if (res.ok) {
            const data = await res.json();
            renderLedger(data);
        }
    } catch (e) {
        console.error("Failed to fetch history:", e);
    }
}

function getBadgeClass(token) {
    const tok = (token || "").toLowerCase();
    if (tok === "fizz") return "fizz";
    if (tok === "buzz") return "buzz";
    if (tok === "fizzbuzz") return "fizzbuzz";
    return "raw";
}

function renderLedger(items) {
    if (!items || items.length === 0) {
        ledgerCountEl.innerText = "0 Cases";
        ledgerListEl.innerHTML = '<div class="ledger-empty">No historical dockets recorded yet.</div>';
        return;
    }

    // Sort strictly by Order of Inquisition descending (id DESC, adjudicated_at DESC)
    const sorted = [...items].sort((a, b) => {
        if (a.id !== undefined && b.id !== undefined && a.id !== b.id) {
            return b.id - a.id;
        }
        if (b.adjudicated_at && a.adjudicated_at && b.adjudicated_at !== a.adjudicated_at) {
            return b.adjudicated_at - a.adjudicated_at;
        }
        return b.case_id.localeCompare(a.case_id, undefined, { numeric: true });
    });

    ledgerCountEl.innerText = `${sorted.length} Recent`;

    ledgerListEl.innerHTML = sorted.map(item => {
        const badgeClass = getBadgeClass(item.emitted_token);
        return `
            <div class="ledger-item" onclick="openArchivesModal('${escapeHtml(item.case_id)}')" title="Click to review in The Archives">
                <div class="ledger-item-left">
                    <span class="ledger-payload">${escapeHtml(item.case_id)}: '${escapeHtml(item.payload)}'</span>
                    <span class="ledger-details">Root: ${item.digital_root} • Glyph: '${item.terminal_glyph}'</span>
                </div>
                <span class="token-badge ${badgeClass}">${escapeHtml(item.emitted_token)}</span>
            </div>
        `;
    }).join("");
}

function buildTranscriptHtml(data) {
    const t = data.transcript || {};
    const dateStr = new Date(data.adjudicated_at * 1000).toLocaleString();

    return `
        <div class="archive-case-banner">
            <div>
                <div class="archive-case-title">${escapeHtml(data.case_id)} — Inbound Payload '${escapeHtml(data.payload)}'</div>
                <div class="archive-case-sub">Digital Root: ${escapeHtml(data.digital_root)} • Terminal Glyph: '${escapeHtml(data.terminal_glyph)}' • Adjudicated: ${escapeHtml(dateStr)}</div>
            </div>
            <span class="token-badge ${getBadgeClass(data.emitted_token)}" style="font-size:0.9rem;padding:4px 10px;">${escapeHtml(data.emitted_token)}</span>
        </div>

        <div class="modal-section bailiff">
            <div class="modal-section-title">Bailiff Bar Docket Proclamation</div>
            <div class="modal-section-text">${escapeHtml(t.bailiff_proclamation || "Court called to order.")}</div>
        </div>

        <div class="modal-section historian">
            <div class="modal-section-title">Court Historian Precedent Entry</div>
            <div class="modal-section-text">${escapeHtml(t.historian_statement || "Record entered.")}</div>
        </div>

        <div class="modal-section judge">
            <div class="modal-section-title">Judge Baz Chamber Release Order</div>
            <div class="modal-section-text">${escapeHtml(t.judge_chamber_order || "Chambers ordered.")}</div>
        </div>

        <div class="modal-section fizz">
            <div class="modal-section-title">Fizz Private Chamber (Behind Closed Doors)</div>
            <div class="modal-section-text">${escapeHtml(t.fizz_caucus_memo || "No memo filed.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Buzz Private Chamber (Behind Closed Doors)</div>
            <div class="modal-section-text">${escapeHtml(t.buzz_caucus_memo || "No memo filed.")}</div>
        </div>

        <div class="modal-section fizz">
            <div class="modal-section-title">Lobbyist-3 Floor Petition</div>
            <div class="modal-section-text">${escapeHtml(t.l3_claim || "No petition filed.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Lobbyist-5 Floor Petition</div>
            <div class="modal-section-text">${escapeHtml(t.l5_claim || "No petition filed.")}</div>
        </div>

        <div class="modal-section auditor">
            <div class="modal-section-title">Forensic Zero-Trust Audit</div>
            <div class="modal-section-text">${escapeHtml(t.audit_verdict || "No audit memo.")}</div>
        </div>

        <div class="modal-section regulator">
            <div class="modal-section-title">Antitrust Market Determination</div>
            <div class="modal-section-text">${escapeHtml(t.antitrust_ruling || "No ruling filed.")}</div>
        </div>

        <div class="modal-section fizz">
            <div class="modal-section-title">Lobbyist-3 Floor Ratification Plea</div>
            <div class="modal-section-text">${escapeHtml(t.l3_plea || "No plea recorded.")}</div>
        </div>

        <div class="modal-section buzz">
            <div class="modal-section-title">Lobbyist-5 Floor Ratification Plea</div>
            <div class="modal-section-text">${escapeHtml(t.l5_plea || "No plea recorded.")}</div>
        </div>

        <div class="modal-section judge">
            <div class="modal-section-title">Judge Baz, Presiding Magistrate Ruling</div>
            <div class="modal-section-text">${escapeHtml(t.judge_baz_order || t.appellate_order || "No decree filed.")}</div>
        </div>

        <div class="modal-section orator">
            <div class="modal-section-title">Constituent Victory Address</div>
            <div class="modal-section-text">${escapeHtml(t.victory_address || "No address delivered.")}</div>
        </div>

        <div class="docket-verdict-card" style="margin-top: 12px;">
            <div class="verdict-card-label">FINAL CERTIFIED CONSENSUS EMISSION</div>
            <div class="verdict-card-token">${escapeHtml(data.emitted_token)}</div>
            <div class="verdict-card-desc">${escapeHtml(data.verdict)}</div>
        </div>
    `;
}

// --- THE ARCHIVES MODAL (ALL PRIORS IN ORDER) ---
async function openArchivesModal(initialCaseId = null) {
    const archivesModalEl = document.getElementById("archives-modal");
    const listPaneEl = document.getElementById("archives-list-pane");
    const summaryMetaEl = document.getElementById("archives-summary-meta");
    if (!archivesModalEl) return;

    archivesModalEl.classList.remove("hidden");
    listPaneEl.innerHTML = '<div class="modal-loading">Loading complete court archives...</div>';

    try {
        const res = await fetch(`/api/archives?order=${encodeURIComponent(archivesOrder)}`);
        if (!res.ok) throw new Error("Failed to load court archives");
        const payload = await res.json();
        allArchivesDockets = payload.dockets || [];

        const fizzCount = allArchivesDockets.filter(d => d.emitted_token === "Fizz").length;
        const buzzCount = allArchivesDockets.filter(d => d.emitted_token === "Buzz").length;
        const fbCount = allArchivesDockets.filter(d => d.emitted_token === "FizzBuzz").length;
        const rawCount = allArchivesDockets.length - fizzCount - buzzCount - fbCount;

        if (summaryMetaEl) {
            summaryMetaEl.innerText = `${allArchivesDockets.length} Total Priors • Fizz: ${fizzCount} • Buzz: ${buzzCount} • FizzBuzz: ${fbCount} • Digits: ${rawCount}`;
        }
        if (ledgerCountEl) {
            ledgerCountEl.innerText = `${allArchivesDockets.length} Priors`;
        }

        renderArchivesList();

        const targetCaseId = initialCaseId || (filteredArchivesDockets[0] && filteredArchivesDockets[0].case_id);
        if (targetCaseId) {
            await selectArchivesDocket(targetCaseId, true);
        }
    } catch (err) {
        listPaneEl.innerHTML = `<div class="modal-error">Error loading The Archives: ${escapeHtml(err.message)}</div>`;
    }
}

function closeArchivesModal() {
    const archivesModalEl = document.getElementById("archives-modal");
    if (archivesModalEl) archivesModalEl.classList.add("hidden");
}

function setArchivesFilter(filterVal) {
    archivesFilter = filterVal;
    const btns = document.querySelectorAll("#archives-filters .archive-filter-btn");
    btns.forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-filter") === filterVal);
    });
    renderArchivesList();
    if (filteredArchivesDockets.length > 0) {
        const stillPresent = filteredArchivesDockets.some(d => d.case_id === selectedArchivesCaseId);
        if (!stillPresent) {
            selectArchivesDocket(filteredArchivesDockets[0].case_id, true);
        } else {
            updateArchivesNavButtons();
        }
    }
}

function toggleArchivesOrder() {
    archivesOrder = archivesOrder === "desc" ? "asc" : "desc";
    const orderBtn = document.getElementById("archives-order-btn");
    if (orderBtn) {
        orderBtn.innerText = archivesOrder === "desc"
            ? "Order: Latest Inquisition First"
            : "Order: 1st Inquisition First";
    }
    allArchivesDockets.sort((a, b) => {
        if (a.id !== undefined && b.id !== undefined && a.id !== b.id) {
            return archivesOrder === "asc" ? a.id - b.id : b.id - a.id;
        }
        if (a.adjudicated_at && b.adjudicated_at && a.adjudicated_at !== b.adjudicated_at) {
            return archivesOrder === "asc" ? a.adjudicated_at - b.adjudicated_at : b.adjudicated_at - a.adjudicated_at;
        }
        return 0;
    });
    renderArchivesList();
    updateArchivesNavButtons();
}

function renderArchivesList() {
    const listPaneEl = document.getElementById("archives-list-pane");
    const searchInputEl = document.getElementById("archives-search-input");
    if (!listPaneEl) return;

    const query = (searchInputEl ? searchInputEl.value : "").trim().toLowerCase();

    filteredArchivesDockets = allArchivesDockets.filter(item => {
        const badgeClass = getBadgeClass(item.emitted_token);
        if (archivesFilter !== "all" && badgeClass !== archivesFilter) {
            return false;
        }
        if (query) {
            const matchPayload = String(item.payload).toLowerCase().includes(query);
            const matchCase = String(item.case_id).toLowerCase().includes(query);
            const matchToken = String(item.emitted_token).toLowerCase().includes(query);
            if (!matchPayload && !matchCase && !matchToken) return false;
        }
        return true;
    });

    if (filteredArchivesDockets.length === 0) {
        listPaneEl.innerHTML = '<div class="ledger-empty">No prior dockets match the current filter.</div>';
        return;
    }

    listPaneEl.innerHTML = filteredArchivesDockets.map((item, idx) => {
        const badgeClass = getBadgeClass(item.emitted_token);
        const isActive = item.case_id === selectedArchivesCaseId ? "active" : "";
        return `
            <div class="archive-list-item ${isActive}"
                 id="archive-item-${escapeHtml(item.case_id)}"
                 onclick="selectArchivesDocket('${escapeHtml(item.case_id)}')">
                <div class="ledger-item-left">
                    <span class="ledger-payload">${escapeHtml(item.case_id)}: '${escapeHtml(item.payload)}'</span>
                    <span class="ledger-details">Root: ${escapeHtml(item.digital_root)} • Glyph: '${escapeHtml(item.terminal_glyph)}'</span>
                </div>
                <span class="token-badge ${badgeClass}">${escapeHtml(item.emitted_token)}</span>
            </div>
        `;
    }).join("");
}

function updateArchivesNavButtons() {
    const prevBtn = document.getElementById("archives-prev-btn");
    const nextBtn = document.getElementById("archives-next-btn");
    const navLabel = document.getElementById("archives-nav-label");
    if (!prevBtn || !nextBtn || !navLabel) return;

    const idx = filteredArchivesDockets.findIndex(d => d.case_id === selectedArchivesCaseId);
    if (idx === -1) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        navLabel.innerText = "Select a docket to review";
        return;
    }

    prevBtn.disabled = idx <= 0;
    nextBtn.disabled = idx >= filteredArchivesDockets.length - 1;
    const item = filteredArchivesDockets[idx];
    navLabel.innerText = `Prior ${idx + 1} of ${filteredArchivesDockets.length} (${item.case_id} • Payload '${item.payload}')`;
}

async function selectArchivesDocket(caseId, scrollIntoView = false) {
    selectedArchivesCaseId = caseId;
    const reviewContentEl = document.getElementById("archives-review-content");

    // Highlight active item in left list
    document.querySelectorAll(".archive-list-item").forEach(el => {
        el.classList.toggle("active", el.id === `archive-item-${caseId}`);
    });
    if (scrollIntoView) {
        const activeEl = document.getElementById(`archive-item-${caseId}`);
        if (activeEl && activeEl.scrollIntoView) {
            activeEl.scrollIntoView({ block: "nearest" });
        }
    }

    updateArchivesNavButtons();

    if (!reviewContentEl) return;
    reviewContentEl.innerHTML = `<div class="modal-loading">Loading transcript for ${escapeHtml(caseId)}...</div>`;

    try {
        const res = await fetch(`/api/docket/${encodeURIComponent(caseId)}`);
        if (!res.ok) {
            reviewContentEl.innerHTML = `<div class="modal-error">Docket ${escapeHtml(caseId)} not found in archives.</div>`;
            return;
        }
        const data = await res.json();
        reviewContentEl.innerHTML = buildTranscriptHtml(data);
        reviewContentEl.scrollTop = 0;
    } catch (e) {
        reviewContentEl.innerHTML = `<div class="modal-error">Error loading docket: ${escapeHtml(e.message)}</div>`;
    }
}

function stepArchivesDocket(delta) {
    const idx = filteredArchivesDockets.findIndex(d => d.case_id === selectedArchivesCaseId);
    if (idx === -1) return;
    const nextIdx = idx + delta;
    if (nextIdx >= 0 && nextIdx < filteredArchivesDockets.length) {
        selectArchivesDocket(filteredArchivesDockets[nextIdx].case_id, true);
    }
}

async function openCaseModal(caseId) {
    modalCaseTitleEl.innerText = caseId;
    modalCaseMetaEl.innerText = "Loading archived record...";
    modalCaseBodyEl.innerHTML = '<div class="modal-loading">Querying SQLite persistent ledger...</div>';
    caseModalEl.classList.remove("hidden");

    try {
        const res = await fetch(`/api/docket/${encodeURIComponent(caseId)}`);
        if (!res.ok) {
            modalCaseBodyEl.innerHTML = `<div class="modal-error">Docket ${escapeHtml(caseId)} not found in archives.</div>`;
            return;
        }

        const data = await res.json();
        const dateStr = new Date(data.adjudicated_at * 1000).toLocaleString();
        modalCaseMetaEl.innerText = `Inbound Payload '${data.payload}' • Digital Root: ${data.digital_root} • Terminal Glyph: '${data.terminal_glyph}' • Adjudicated: ${dateStr}`;
        modalCaseBodyEl.innerHTML = buildTranscriptHtml(data);
    } catch (e) {
        modalCaseBodyEl.innerHTML = `<div class="modal-error">Error loading docket: ${escapeHtml(e.message)}</div>`;
    }
}

function closeCaseModal() {
    caseModalEl.classList.add("hidden");
}

window.addEventListener("click", (e) => {
    if (e.target === caseModalEl) {
        closeCaseModal();
    }
    const archivesModalEl = document.getElementById("archives-modal");
    if (archivesModalEl && e.target === archivesModalEl) {
        closeArchivesModal();
    }
});

function reconnectObserver() {
    standbyOverlayEl.classList.add("hidden");
    sendVisibilityHeartbeat();
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

const AMAZON_ASSOCIATE_TAG = "adamoutler-20";
const AMAZON_CATALOG = [
    {
        icon: "⚡",
        title: "Local LLM Inference GPUs & AI Rigs",
        desc: "Power 17-agent Ollama swarms locally with zero cloud token bills.",
        cta: "Shop on Amazon \u2192",
        query: "nvidia+rtx+gpu+local+ai+workstation"
    },
    {
        icon: "\uD83D\uDC68\u200D\u2696\uFE0F",
        title: "Presiding Magistrate Hardwood Gavel Set",
        desc: "Overrule remand petitions and dissolve stays at your desk with prejudice.",
        cta: "View on Amazon \u2192",
        query: "judge+gavel+and+block+set+solid+wood"
    },
    {
        icon: "\uD83D\uDDA5\uFE0F",
        title: "Ryzen AI & Homelab Mini PCs (64GB RAM)",
        desc: "Compact silent server nodes for 24/7 Docker & multi-agent orchestration.",
        cta: "View on Amazon \u2192",
        query: "ryzen+ai+mini+pc+64gb+ram+homelab"
    },
    {
        icon: "\uD83D\uDCDA",
        title: "Designing Data-Intensive Applications",
        desc: "Master Byzantine fault tolerance, consensus algorithms, and distributed state.",
        cta: "View on Amazon \u2192",
        query: "designing+data+intensive+applications+book"
    },
    {
        icon: "\u2328\uFE0F",
        title: "Keychron Custom Mechanical Keyboards",
        desc: "Draft adversarial floor petitions and appellate briefs at maximum WPM.",
        cta: "Shop on Amazon \u2192",
        query: "keychron+q+series+mechanical+keyboard"
    },
    {
        icon: "\uD83D\uDCBE",
        title: "4TB Gen4/Gen5 NVMe SSDs for Vector DBs",
        desc: "High-IOPS persistent storage for SQLite ledgers and LLM model weights.",
        cta: "View on Amazon \u2192",
        query: "samsung+990+pro+4tb+nvme+ssd"
    }
];
let amazonPairIndex = 0;

function rotateAmazonAds() {
    const gridEl = document.getElementById("amazon-items-grid");
    if (!gridEl) return;
    amazonPairIndex = (amazonPairIndex + 2) % AMAZON_CATALOG.length;
    const items = [
        AMAZON_CATALOG[amazonPairIndex],
        AMAZON_CATALOG[(amazonPairIndex + 1) % AMAZON_CATALOG.length]
    ];
    gridEl.innerHTML = items.map(item => `
        <a href="https://www.amazon.com/s?k=${item.query}&amp;tag=${AMAZON_ASSOCIATE_TAG}"
           target="_blank"
           rel="nofollow sponsored noopener"
           class="amazon-product-item">
            <div class="amazon-item-top">
                <span class="amazon-item-icon">${item.icon}</span>
                <div class="amazon-item-info">
                    <div class="amazon-item-title">${escapeHtml(item.title)}</div>
                    <div class="amazon-item-desc">${escapeHtml(item.desc)}</div>
                </div>
            </div>
            <span class="amazon-cta-btn">${escapeHtml(item.cta)}</span>
        </a>
    `).join("");
}

window.rotateAmazonAds = rotateAmazonAds;
window.openArchivesModal = openArchivesModal;
window.closeArchivesModal = closeArchivesModal;
window.setArchivesFilter = setArchivesFilter;
window.toggleArchivesOrder = toggleArchivesOrder;
window.renderArchivesList = renderArchivesList;
window.selectArchivesDocket = selectArchivesDocket;
window.stepArchivesDocket = stepArchivesDocket;

window.addEventListener("DOMContentLoaded", () => {
    connectWebSocket();
});
