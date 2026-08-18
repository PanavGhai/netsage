const $ = (id) => document.getElementById(id);

const API_BASE =
    window.location.port === "5000"
        ? ""
        : "http://127.0.0.1:5000";

const caseSelect = $("case-select");
const diagnoseButton = $("diagnose-button");
const submitReviewButton = $("submit-review-button");

const decisionButtons = {
    Accepted: $("accept-button"),
    Edited: $("edit-button"),
    Rejected: $("reject-button")
};

let cases = [];
let selectedCase = null;
let selectedReviewDecision = null;
let currentAiResponse = null;
function msg(text = "", info = false) {
    const el = $("page-message");

    el.textContent = text;
    el.hidden = !text;
    el.classList.toggle("is-info", info);
}

function badge(id, text, kind = "neutral") {
    const el = $(id);

    el.textContent = text;
    el.className = "status-badge status-" + kind;
}

function workflow(step) {
    document.querySelectorAll(".workflow-step").forEach((el, i) => {
        el.classList.toggle("is-active", i + 1 === step);
        el.classList.toggle("is-complete", i + 1 < step);
    });
}

function reviewEnabled(enabled) {
    Object.values(decisionButtons).forEach((button) => {
        button.disabled = !enabled;
    });

    $("review-notes").disabled = !enabled;
    submitReviewButton.disabled = !enabled;
}

function reset() {
    currentAiResponse = null;
    selectedReviewDecision = null;

    [
        "root-cause",
        "confidence",
        "osi-layer",
        "evidence",
        "next-command",
        "fix-steps"
    ].forEach((id) => {
        $(id).textContent = "—";
    });

    $("root-cause").hidden = false;
    $("edited-root-cause").hidden = true;
    $("edited-root-cause").value = "";
    $("review-notes").value = "";

    Object.values(decisionButtons).forEach((button) => {
        button.classList.remove("is-selected");
    });

    reviewEnabled(false);

    badge(
        "diagnosis-status",
        selectedCase ? "READY TO ANALYZE" : "AWAITING CASE",
        selectedCase ? "info" : "neutral"
    );

    badge("review-status", "AWAITING AI DIAGNOSIS");
    badge("verification-status", "PENDING", "pending");

    $("verification-message").textContent =
        "Submit a human review to receive a verification result.";
}

function loadCase() {
    selectedCase =
        cases.find((item) => item.case_id === caseSelect.value) || null;

    reset();
    msg();

    $("symptoms").value = selectedCase?.symptom || "";
    $("topology-notes").value = selectedCase?.topology || "";
    $("show-output").value = selectedCase?.show_output || "";

    diagnoseButton.disabled = !selectedCase;

    badge(
        "case-status",
        selectedCase ? selectedCase.case_id : "NO CASE SELECTED",
        selectedCase ? "info" : "neutral"
    );

    workflow(selectedCase ? 2 : 1);
}

function showDiagnosis(data) {
    const result = data.ai_response;

    currentAiResponse = result;

    $("root-cause").textContent = result.root_cause || "—";
    $("confidence").textContent = result.confidence || "—";
    $("osi-layer").textContent = result.osi_layer || "—";

    $("evidence").textContent =
        (result.evidence || []).join("\n") || "—";

    $("next-command").textContent =
        result.next_command || "—";

    $("fix-steps").textContent =
        (result.fix_steps || []).join("\n") || "—";

    badge("diagnosis-status", "AI RECOMMENDATION", "info");
    badge("review-status", "AWAITING HUMAN REVIEW", "pending");

    reviewEnabled(true);
    workflow(3);
}
async function api(url, body, label) {
    let response;

    try {
        response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });
    } catch {
        throw Error(
            "Backend unavailable while " +
            label.toLowerCase() +
            ". Start the NetSage backend and try again."
        );
    }

    let data;

    try {
        data = await response.json();
    } catch {
        throw Error(label + " returned an invalid response.");
    }

    if (!response.ok) {
        throw Error(data.error || label);
    }

    return data;
}

async function getApi(url, label) {
    let response;

    try {
        response = await fetch(url);
    } catch {
        throw Error(label + " is unavailable.");
    }

    if (!response.ok) {
        throw Error(label + " could not be loaded.");
    }

    return response.json();
}

function renderBars(id, values, modifier = "") {
    const container = $(id);
    const entries = Object.entries(values || {});
    const max = Math.max(...entries.map(([, value]) => value), 1);

    container.replaceChildren();

    entries.forEach(([label, value]) => {
        const row = document.createElement("div");
        const name = document.createElement("span");
        const track = document.createElement("div");
        const fill = document.createElement("div");
        const count = document.createElement("strong");

        row.className = "bar-row";
        name.className = "bar-label";
        name.textContent = label;
        track.className = "bar-track";
        fill.className = "bar-fill " + modifier;
        fill.style.width = (value / max) * 100 + "%";
        count.textContent = value;

        track.appendChild(fill);
        row.append(name, track, count);
        container.appendChild(row);
    });
}

async function loadDashboard() {
    try {
        const metrics = await getApi(API_BASE + "/api/dashboard", "Dashboard metrics");

        renderBars("issue-types-chart", metrics.issue_types);
        renderBars("severity-chart", metrics.severity_distribution, "severity");
        renderBars("review-decisions-chart", metrics.review_decisions, "reviews");

        const agreement = metrics.agreement;
        const summary = $("agreement-summary");

        if (agreement.rate === null) {
            badge("agreement-rate", "NO REVIEWS YET");
            summary.textContent = "No human reviews recorded yet.";
        } else {
            badge("agreement-rate", agreement.rate + "% AGREEMENT", "approved");
            summary.textContent = agreement.rate + "% agreement (" +
                agreement.accepted + " accepted of " + agreement.reviewed + " reviews)";
        }

        const groundTruth = metrics.ground_truth;
        const groundTruthAccuracy = $("ground-truth-accuracy");
        const groundTruthSummary = $("ground-truth-summary");

        if (groundTruth && groundTruth.evaluated > 0) {
            groundTruthAccuracy.textContent =
                groundTruth.accuracy + "% accuracy";

            groundTruthSummary.textContent =
                groundTruth.matches + " of " +
                groundTruth.evaluated +
                " AI diagnoses matched the expected fault.";
        } else {
            groundTruthAccuracy.textContent = "No evaluation data yet.";
            groundTruthSummary.textContent =
                "Ground-truth evaluation is not available.";
        }
    } catch {
        badge("agreement-rate", "METRICS UNAVAILABLE", "blocked");

        $("agreement-summary").textContent =
            "Start the NetSage backend to load dashboard metrics.";

        $("ground-truth-accuracy").textContent =
            "Metrics unavailable.";

        $("ground-truth-summary").textContent =
            "Start the NetSage backend to load ground-truth evaluation.";
    }
}

function config() {
    return {
        ip: $("ip-address").value.trim(),
        mask: $("subnet-mask").value.trim(),
        gateway: $("default-gateway").value.trim()
    };
}

async function diagnose() {
    if (!selectedCase) {
        return msg("Select a case before running a diagnosis.");
    }

    msg("Analyzing case…", true);

    diagnoseButton.disabled = true;
    diagnoseButton.textContent = "Analyzing case…";

    badge("diagnosis-status", "ANALYZING", "pending");

    try {
        showDiagnosis(
            await api(
                API_BASE + "/api/diagnose",
                {
                    case: selectedCase,
                    config: config()
                },
                "Diagnosis failed"
            )
        );

        msg();
    } catch (error) {
        badge("diagnosis-status", "DIAGNOSIS FAILED", "blocked");
        msg(error.message);
    } finally {
        diagnoseButton.disabled = !selectedCase;
        diagnoseButton.textContent = "Run AI diagnosis";
    }
}

function choose(decision) {
    if (!currentAiResponse) {
        return msg(
            "Run an AI diagnosis before choosing a review decision."
        );
    }

    selectedReviewDecision = decision;

    Object.entries(decisionButtons).forEach(([key, button]) => {
        button.classList.toggle("is-selected", key === decision);
    });

    const editing = decision === "Edited";

    $("root-cause").hidden = editing;
    $("edited-root-cause").hidden = !editing;

    if (editing) {
        $("edited-root-cause").value =
            $("root-cause").textContent === "—"
                ? ""
                : $("root-cause").textContent;

        $("edited-root-cause").focus();
    }

    badge(
        "review-status",
        "HUMAN " + decision.toUpperCase(),
        decision === "Rejected"
            ? "rejected"
            : decision === "Edited"
                ? "edited"
                : "approved"
    );

    msg();
}

async function submit() {
    if (!currentAiResponse) {
        return msg("Run an AI diagnosis before submitting a review.");
    }

    if (!selectedReviewDecision) {
        return msg(
            "Choose Accept, Edit, or Reject before submitting the review."
        );
    }

    const cause =
        selectedReviewDecision === "Edited"
            ? $("edited-root-cause").value.trim()
            : $("root-cause").textContent;

    if (selectedReviewDecision === "Edited" && !cause) {
        return msg(
            "A corrected root cause is required when editing a diagnosis."
        );
    }

    msg("Submitting human review…", true);

    submitReviewButton.disabled = true;
    submitReviewButton.textContent = "Submitting review…";

    try {
        const data = await api(
            API_BASE + "/api/review",
            {
                case: selectedCase,
                config: config(),
                ai_response: currentAiResponse,
                review_decision: selectedReviewDecision,
                final_root_cause: cause,
                note: $("review-notes").value.trim()
            },
            "Review submission failed"
        );

        const decision = data.review.decision;
        const verification = data.verification;

        badge(
            "review-status",
            "HUMAN " + decision.toUpperCase(),
            decision === "Rejected"
                ? "rejected"
                : decision === "Edited"
                    ? "edited"
                    : "approved"
        );

        badge(
            "verification-status",
            verification.status.toUpperCase(),
            verification.status.toLowerCase() === "approved"
                ? "approved"
                : "blocked"
        );

        $("verification-message").textContent =
            verification.reason || "Verification completed.";

        workflow(4);
        reviewEnabled(false);
        loadDashboard();
        msg();
    } catch (error) {
        msg(error.message);
        submitReviewButton.disabled = false;
    } finally {
        submitReviewButton.textContent = "Submit human review";
    }
}

async function loadCases() {
    try {
        const response = await fetch("/data/cases.json");

        if (!response.ok) {
            throw Error();
        }

        cases = await response.json();

        caseSelect.innerHTML =
            '<option value="">Select a case</option>';

        cases.forEach((item) => {
            const option = document.createElement("option");

            option.value = item.case_id;
            option.textContent =
                item.case_id + " — " + item.concept;

            caseSelect.appendChild(option);
        });

        caseSelect.disabled = false;

        $("system-status").textContent =
            cases.length + " cases available";
    } catch {
        caseSelect.innerHTML =
            '<option value="">Case data unavailable</option>';

        $("system-status").textContent =
            "Case library unavailable";

        msg(
            "Case data failed to load. Serve the frontend through " +
            "the NetSage application and refresh."
        );
    }
}

diagnoseButton.addEventListener("click", diagnose);

caseSelect.addEventListener("change", loadCase);

Object.entries(decisionButtons).forEach(([decision, button]) => {
    button.addEventListener("click", () => choose(decision));
});

submitReviewButton.addEventListener("click", submit);

loadCases();
loadDashboard();
