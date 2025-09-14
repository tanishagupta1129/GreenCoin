document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("proofForm");
    const activityField = document.getElementById("activity");

    const plantingSteps = document.getElementById("planting-steps");
    const proofField = document.getElementById("proof-field");

    function toggleFields() {
        const activity = activityField.value;
        if (activity === "Tree Plantation") {
            plantingSteps.style.display = "block";
            proofField.style.display = "none";
        } else {
            plantingSteps.style.display = "none";
            proofField.style.display = "block";
        }
    }

    function previewImage(input, previewId) {
        const file = input.files[0];
        const preview = document.getElementById(previewId);
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            preview.style.display = 'none';
        }
    }

    function checkSize(input) {
        const file = input.files[0];
        const maxSize = 2 * 1024 * 1024; // 2MB
        if (file && file.size > maxSize) {
            alert("File too large. Maximum allowed size is 2MB.");
            input.value = '';
        }
    }

    // Hook events
    toggleFields();
    activityField.addEventListener("change", toggleFields);

    const proofInput = document.querySelector('input[name="proof_image"]');
    const actionInput = document.getElementById("image_action");
    const afterPlantingInput = document.getElementById("image_after_planting");

    if (proofInput) {
        proofInput.addEventListener("change", function () {
            previewImage(this, 'preview_proof');
            checkSize(this);
        });
    }

    if (actionInput) {
        actionInput.addEventListener("change", function () {
            previewImage(this, 'preview_action');
            checkSize(this);
        });
    }

    if (afterPlantingInput) {
        afterPlantingInput.addEventListener("change", function () {
            previewImage(this, 'preview_after');
            checkSize(this);
        });
    }

    // Email verification is optional — add if needed.
});
