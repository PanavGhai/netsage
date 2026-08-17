const caseSelect = document.getElementById("case-select");

const diagnoseButton = document.getElementById("diagnose-button");

const acceptButton = document.getElementById("accept-button");
const editButton = document.getElementById("edit-button");
const rejectButton = document.getElementById("reject-button");

const submitReviewButton = document.getElementById("submit-review-button");

let cases = [];
let selectedCase = null;
let selectedReviewDecision = null;

async function loadCases() {
    const response = await fetch("/data/cases.json");

    if (!response.ok) {
        throw new Error("Could not load cases");
    }

    cases = await response.json();

    for (const item of cases) {
        const option = document.createElement("option");

        option.value = item.case_id;
        option.textContent = item.case_id + " - " + item.concept;

        caseSelect.appendChild(option);
    }
}

function loadSelectedCase() {
    selectedCase = cases.find(
        item => item.case_id === caseSelect.value
    );

    if (!selectedCase) {
        return;
    }

    document.getElementById("symptoms").value =
        selectedCase.symptom;

    document.getElementById("topology-notes").value =
        selectedCase.topology;

    document.getElementById("show-output").value =
        selectedCase.show_output;
}

function setReviewStatus(status) {
    document.getElementById("review-status").textContent = status;
}


function showDiagnosis(data) {
    const result = data.ai_response;

    document.getElementById("root-cause").textContent =
        result.root_cause || "-";

    document.getElementById("confidence").textContent =
        result.confidence || "-";

    document.getElementById("osi-layer").textContent =
        result.osi_layer || "-";

    document.getElementById("evidence").textContent =
        (result.evidence || []).join(", ");

    document.getElementById("next-command").textContent =
        result.next_command || "-";

    document.getElementById("fix-steps").textContent =
        (result.fix_steps || []).join(", ");
}


async function diagnoseCase() {
    if (!selectedCase) {
        alert("Select a case first.");
        return;
    }

    const caseData = selectedCase;

    const config = {
        ip: document.getElementById("ip-address").value,
        mask: document.getElementById("subnet-mask").value,
        gateway: document.getElementById("default-gateway").value
    };

    try {
        const response = await fetch("http://127.0.0.1:5000/api/diagnose", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                case: caseData,
                config: config
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Diagnosis failed");
        }

        showDiagnosis(data);

    } catch (error) {
        console.error(error);
        alert("Unable to connect to NetSage backend.");
    }
}


diagnoseButton.addEventListener("click", diagnoseCase);
caseSelect.addEventListener("change", loadSelectedCase);


acceptButton.addEventListener("click", function () {
    selectedReviewDecision = "Accepted";
    setReviewStatus("Accepted");
});


editButton.addEventListener("click", function () {
    selectedReviewDecision = "Edited";
    setReviewStatus("Edited");
});


rejectButton.addEventListener("click", function () {
    selectedReviewDecision = "Rejected";
    setReviewStatus("Rejected");
});


async function submitReview() {
    if (!selectedCase) {
        alert("Select a case first.");
        return;
    }

    if (!selectedReviewDecision) {
        alert("Select Accept, Edit, or Reject first.");
        return;
    }

    const config = {
        ip: document.getElementById("ip-address").value,
        mask: document.getElementById("subnet-mask").value,
        gateway: document.getElementById("default-gateway").value
    };

    const finalRootCause =
        document.getElementById("root-cause").textContent;

    const note =
        document.getElementById("review-notes").value;

    try {
        const response = await fetch("http://127.0.0.1:5000/api/review", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                case: selectedCase,
                config: config,
                review_decision: selectedReviewDecision,
                final_root_cause: finalRootCause,
                note: note
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Review submission failed");
        }

        setReviewStatus(
            data.verification.status
        );

        console.log("Review submitted:", data);

    } catch (error) {
        console.error(error);
        alert("Unable to submit review.");
    }
}

submitReviewButton.addEventListener("click", submitReview);

loadCases().catch(error => {
    console.error(error);
});