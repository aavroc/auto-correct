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

function XXXaddImage(src, id, text) {
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

function XXXaddPdf(source, id) {
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

function focusInputField(targetId, points_possible, rating_prefix, comment_prefix ) {
    var rating = document.getElementById( rating_prefix  + targetId );
    var feedback = document.getElementById( comment_prefix  + targetId );
    var oldValue = parseFloat(rating.value);

    if ( feedback.value[0] == '#' ) {
        referer = feedback.value.slice(1);
        referer_rating = document.getElementById( rating_prefix  + referer );
        referer_feedback = document.getElementById( comment_prefix  + referer );
        if ( referer_rating ) {
            rating.value = referer_rating.value;
            feedback.value = referer_feedback.value;
        }
        return
    }

    feedback_words = feedback.value.split(" ");
    feedback_last_word = feedback_words[feedback_words.length - 1];
    proposed_score = parseInt(feedback_last_word);
    name_of_feedback = feedback.value.substring(0, 60);

    if (!isNaN(proposed_score) && proposed_score.toString() === feedback_last_word) {
        // add feedback to drop down
        itemNr = 1
        while ( selectElement = document.getElementById( 'comments_' + itemNr ) ) {
            newOption = document.createElement("option");
            newOption.value = feedback.value;
            newOption.text = feedback.value;
            selectElement.appendChild(newOption);
            itemNr += 1;
        } 

        // Fill in proposed score plus remove last interger from feedback
        rating.value = proposed_score;
        feedback_words.pop();
        feedback.value = feedback_words.join(" ");

        return
    }


    if ( oldValue != points_possible ) { // when value is lower than max, don;t change it again
        return
    }
    var newValue = Math.floor(points_possible * 0.25);

    if (!isNaN(oldValue)) {
        rating.value = newValue;

        var flickeringInterval = setInterval(function () {
            rating.value = (rating.value === "") ? newValue : "";
        }, 100);

        setTimeout(function () {
            clearInterval(flickeringInterval);
            rating.value = newValue;
            rating.focus();
            rating.select();
        }, 300);
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
    var currentValue = parseInt( inputField.value, 10 );
    var maxValue = parseInt( maxValue );

    if ( maxValue > 5 ) {
        step = 2;
    } else {
        step = 1;
    }
    
    if ( currentValue + step > maxValue ) {
        if ( currentValue != maxValue ) {
            inputField.value = maxValue;
        } else {
            inputField.value = 0;
        }
    } else {
        inputField.value = currentValue + step;
    }
}

function updateRatingField(itemNr, selectedValue) {
    var feedbackId = 'feedback_' + itemNr;
    var feedback = document.getElementById(feedbackId);

    var ratingId = 'rating_' + itemNr;
    var rating = document.getElementById(ratingId);

    feedback_words = selectedValue.split(" ");
    feedback_last_word = feedback_words[feedback_words.length - 1];
    proposed_score = parseInt(feedback_last_word);

    if (!isNaN(proposed_score) && proposed_score.toString() === feedback_last_word) {
        rating.value = proposed_score;
        feedback_words.pop();
        feedback.value = feedback_words.join(" ");
    } else {
        rating.value = 0;
        feedback.value = selectedValue;
    }
}