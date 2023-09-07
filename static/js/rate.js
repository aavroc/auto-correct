function updateCheckboxValue(i) {
    var visibleCheckbox = document.getElementById("cb_" + i);
    var hiddenCheckboxValue = document.getElementById("hidden_checkbox_" + i);

    if (visibleCheckbox.checked) {
        hiddenCheckboxValue.value = "1";
    } else {
        hiddenCheckboxValue.value = "0";
    }
}

function uncheckCheckBox(i) {
    var visibleCheckbox = document.getElementById("cb_" + i);
    var hiddenCheckboxValue = document.getElementById("hidden_checkbox_" + i);
    visibleCheckbox.checked = false;
    hiddenCheckboxValue.value = 0;
}

function toggleFullSize(node) {
    node.classList.toggle('fullsize');
}

function addImage(src, id, text) {
    var img = document.createElement('img');

    img.src = src;
    img.onclick = function () { toggleFullSize(this); };
    img.alt = 'Uploaded additional Image';

    var target = document.getElementById(id);

    var span = document.createElement('span');
    span.className = 'small-grey';
    var fileName = document.createTextNode(text);
    span.appendChild(fileName);

    target.prepend(document.createElement('br'));
    target.prepend(span);
    target.prepend(document.createElement('br'));
    target.prepend(img);
    
}

function addPdf(source, id) {
    // Create new embed element
    var iframe = document.createElement('iframe');

    // Create new a element
    var link = document.createElement('a');

    // Set the attributes
    iframe.src = source;
    iframe.type = "application/pdf";


    link.href = source;
    link.class = "small-link";
    link.textContent = "Open PDF";

    // Find the target div and append the new element to it
    var target = document.getElementById(id);
    target.prepend(document.createElement('br'))
    target.prepend(link);
    target.prepend(document.createElement('br'))
    target.prepend(iframe);
}

function expandTextField(element) {
    if (element.classList.contains("expanded")) {
        element.classList.remove("expanded");
    } else {
        element.classList.add('expanded');
    }
}

function focusInputField(targetId, points_possible) {
    var target = document.getElementById(targetId);
    var oldValue = parseFloat(target.value);
    var newValue = Math.floor(points_possible * 0.25);

    if (!isNaN(oldValue)) {
        target.value = newValue;

        var flickeringInterval = setInterval(function () {
            target.value = (target.value === "") ? newValue : "";
        }, 100);

        setTimeout(function () {
            clearInterval(flickeringInterval);
            target.value = newValue;
            target.focus();
            target.select();
        }, 400);
    }
}

function rateViaCanvas(itemNr, course, assignment, user) {
    uncheckCheckBox(itemNr);
    url = "https://talnet.instructure.com/courses/" + course + "/gradebook/speed_grader?assignment_id=" + assignment + "&student_id=" + user;
    console.log(url);
    window.open(url, '_blank');
}

function setFeedbackAndRating(itemNr, alt_feedback, maxRating) {
    console.log('alt_feedback: ' + alt_feedback);
    var feedbackId = 'feedback_' + itemNr;
    var ratingId = 'rating_' + itemNr;
    var buttonId = 'button_rate_' + itemNr;

    var button = document.getElementById(buttonId);
    button.style.display = 'none';

    var feedbackTextarea = document.getElementById(feedbackId);
    if (feedbackTextarea) {
        feedbackTextarea.value = alt_feedback;
    }

    var ratingInput = document.getElementById(ratingId);
    if (ratingInput) {
        ratingInput.value = maxRating;
    }
}

function decreaseValue(inputField, maxValue) {
    var currentValue = parseInt(inputField.value, 10);
    
    if ( currentValue === parseInt(maxValue) ) {
        inputField.value = 0;
    } else {
        if ( currentValue > 5 ) {
            inputField.value = currentValue + 2;
        } else {
            inputField.value = currentValue + 1;
        }
    }
}

function updateRatingField(itemNr, selectedValue) {
    var feedbackId = 'feedback_' + itemNr;
    var feedback = document.getElementById(feedbackId);

    var ratingId = 'rating_' + itemNr;
    var rating = document.getElementById(ratingId);

    feedback.value = selectedValue;
    rating.value = 0;
}