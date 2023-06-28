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

function toggleFullSize(img) {
    img.classList.toggle('fullsize');
}

function addImage(src, id) {
    var img = document.createElement('img');

    img.src = src;
    img.onclick = function () { toggleFullSize(this); };
    img.alt = 'Uploaded additional Image';

    var target = document.getElementById(id);
    target.prepend(document.createElement('br'))
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


    link.href=source;
    link.class="small-link";
    link.textContent="Open PDF";

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

function focusInputField(target, points_possible) {
    var oldValue = parseFloat(target.value);
    var newValue = Math.floor(points_possible*0.25);

    if (!isNaN(oldValue)) {
        target.value = newValue;

        var flickeringInterval = setInterval(function() {
            target.value = (target.value === "") ? newValue : "";
        }, 100);
      
        setTimeout(function() {
            clearInterval(flickeringInterval);
            target.value = newValue;
            target.focus();
            target.select();
        }, 1200);
    }
}

function rateViaCanvas(itemNr, course, assignment, user) {
    uncheckCheckBox(itemNr);
    url = "https://talnet.instructure.com/courses/"+course+"/gradebook/speed_grader?assignment_id="+assignment+"&student_id="+user;
    console.log(url);
    window.open(url, '_blank');
}