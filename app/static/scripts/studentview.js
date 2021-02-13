// Fetches all the session info from the API (for the teacher)
function fetchSessionInfoTeacher(course_id, session_id, status) {
    let url = "/classes/course/session/" + session_id + "/session_json";
    console.log("HELLO TEACHER")
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => displayAll(status, data)) // Calls the displayData function, which will update the thermometer visually
        .catch(handleError);
}

// Fetches all the session info from the API (for the student)
function fetchSessionInfoStudent(course_id, session_id, status) {
    let url = "/classes/course/session/" + session_id + "/session_json";
    console.log("HELLO STUDENT")
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => displaySome(status, data, session_id)) // Calls the displayData function, which will update the thermometer visually
        .catch(handleError);
}

// Fetches information from PAST sessions
function fetchPastSessionInfo(course_id, session_id, status) {
    let url = "/classes/course/session/" + session_id + "/session_json";
    console.log("PAST INFO FETCHED")
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => displayPast(status, data)) // Calls the displayData function, which will update the thermometer visually
        .catch(handleError);
}

// Fetches information for all of the forms
function fetchSessionFormsInfo(course_id, session_id, status) {
    let url = "/classes/course/session/" + session_id + "/session_forms_json";
    console.log("FORMS INFO FETCHED");
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => displayForms(status, data)) // Calls the displayForms function, which will update the form data visually
        .catch(handleError);
}

// Fetches users in the course
function fetchCourseInfo(course_id) { 
    let url = "/classes/course/" + course_id + "/manage/course_json";
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => displayCourseInfo(data, course_id)) // Data passed into function displayCourseInfo
        .catch(handleError); 
}

// Function for displaying the course information
function displayCourseInfo(data, course_id) {
    console.log("COURSE INFO DISPLAYED");
    displayStudents(data["students"], course_id);
}

function confirm_message(username) {
    if (confirm("Are you sure you want to remove " + username + "?" )) {
        return true;
    } else {
        return false;
    }
    
}

// Displaying the students in the course
function displayStudents(studentInfo, course_id) {
    studentHTML = document.getElementById("studentRow");
    console.log("Students")
    studentHTML.innerHTML = '<tr class = "heading">' + '<th>Username</th>' + 
                                    '<th>Email</th>' + 
                                    '<th>Actions</th>' + 
                            '</tr>'; // clearing all the content in the div
    for (s = 0; s < studentInfo.length; s++) {
        console.log("WOOT")
        var student_username = studentInfo[s]["username"] // Getting the student's username
        var student_email = studentInfo[s]["email"] // Getting the student's email
        var student_id = studentInfo[s]["student_id"] // Getting the student's ID
        studentHTML.innerHTML += ('<tr class = "studentRowEach"><td class="usernameHolder">' + student_username + '</td>' +
                                    '<td class="emailHolder">' + student_email + '</td>' + 
                                    '<td class="removeUserHolder">' + 
                                        '<form action="/classes/course/' + course_id + '/manage/remove/' + student_id + '"method="POST">' +
                                            '<button type="submit" class = "removeButton" onclick="return confirm_message(' + "'"+ student_username + "'" + ')">Remove Student</button>' +
                                        '</form>' +
                                    '</td></tr>')
    }
}

// Calls functions to display the PAST information
function displayPast(status, data) {
    console.log("DISPLAYED");
    displayPercentage(data["percentage"]); // Displays the percentage on the thermometer
}

// Calls function to display the FORMS information
function displayForms(status, data) {
    console.log("DISPLAYED FORMS");
    displayFormResultsAll(data); 
}


// Calls all the separate functions that display each feature, also includes the funtion that checks whether page will be refreshed
function displayAll(status, data) {
    checkIfShouldRefresh(status, data["course_status"]); // Checks whether to refresh the page
    displayPercentage(data["percentage"]); // Display percentage on the thermometer
    console.log(data["percentage"]);
    displayReactions(data["reactions"]); // Display emotions
    displaySpeeds(data["speeds"]); // Display speeds
    displayCalculatedSpeed(data["speed_num"]); // Display the calculated speed number
    displayAttendance(data["attendance"]); // Display the attendance
    // console.log("Passed to displaFormResults: "+ data["forms"][data["forms"].length - 1]["responses"])
    displayFormResults(data["forms"][data["forms"].length - 1]); // Display the Forms responses
}

// Only calls some of the functions to display certain features for the student
function displaySome(status, data, session_id) { 
    checkIfShouldRefresh(status, data["course_status"]); // To check whether to refresh
    displayPercentage(data["percentage"]);  // For the percentage
    displayCalculatedSpeed(data["speed_num"]); // For the speed bunnies
    if (data["forms"].length != 0) {
        displayFormLink(data["forms"], session_id);
    }
}


// Checks whether the page should be refreshed, oldStatus is the status passed in via init function, newStatus is the updated status in the API
function checkIfShouldRefresh(oldStatus, newStatus) {
    if (oldStatus != newStatus) {  // If oldStatus is not equal to newStatus
        console.log("SHOULD REFRESH THE PAGE", oldStatus, newStatus);
        location.reload(); // Then reload the page, and everyone should be kicked out
    }
}

function checkStatus(response) {
    if (!response.ok) { // If the response has caused an error
        throw Error("Error in request: " + response.statusText); // Throw the error and print the description of the text 
    }
    return response; // If it was successful, it will return the response's text
}

function displayPercentage(data) { 
    console.log(data); // shows the percent number in the console, the data is the percentage, e.g. 50 or 33.333
    updateThermometer(data);// Calls the updateThermometer function, which updates the thermometer's height 
}

function displayFormLink(formData, session_id) {
    studentFormHTML = document.getElementById("formHolder"); // getting the HTML element for the forms button
    document.getElementById("formHolder").innerHTML = ""; // clearing all content inside the div first
    console.log("DISPLAY FORM LINK")
    if (formData.length != 0) {
        var form_url = formData[0]["forms_url"]
        studentFormHTML.innerHTML += ('<a href="' + form_url + '">Respond to Form</a>');
    }
}

//<a href="{{ url_for(' + "'" + 'form_response' + "'" + ', session_id=' + '' + session_id + ') }}

function handleError(err) {
    console.log("Ran into error:", err);
}

function updateThermometer(temp) {
    thermometer = document.getElementsByClassName("thermometer"); // Returns an array of elements with that class name
    room_vibe = document.getElementById("room_vibe"); // Grabs the HTML div that will display the overall room vibe
    room_vibe.innerHTML = ""; // Clearing everything in the room_vibe div
    if (temp > 67) {
        console.log("Happy Room Vibe");
        room_vibe.innerHTML += ('<img id = "vibe" class = "teacherStuff" src="../../../../static/images/HappyShadow.png">');
        room_vibe.innerHTML += ('<h2 class = "vibeHeader teacherVibeHeader">Happy Room Vibes!</h2>');
    } else if (temp > 34) {
        console.log("Meh Room Vibe");
        room_vibe.innerHTML += ('<img id = "vibe" class = "teacherStuff" src="../../../../static/images/MehShadow.png">');
        room_vibe.innerHTML += ('<h2 class = "vibeHeader teacherVibeHeader">Unamused Room Vibes...</h2>');
    } else if (temp > 0) {
        console.log("Sad Room Vibe");
        room_vibe.innerHTML += ('<img id = "vibe" class = "teacherStuff" src="../../../../static/images/SadShadow2.png">');
        room_vibe.innerHTML += ('<h2 class = "vibeHeader teacherVibeHeader">Struggling Room Vibes!</h2>');
    } else {
        console.log("No Room Vibe");
        room_vibe.innerHTML += ('<img id = "vibe" class = "teacherStuff" src="../../../../static/images/NoneShadow.png">');
        room_vibe.innerHTML += ('<h2 class = "vibeHeader teacherVibeHeader">No Room Vibes Yet</h2>');
    }
    console.log("Thermometer" + thermometer[0]) 
    console.log("Temperature: " + temp)
    thermometer[0].style.height = temp + "%"; // Changes the height of the thermometer div to the temp value
}

// Page won't refresh when user reacts, submits/posts reactions to the database
function submitFormGeneral(session_id, react_num) {
    console.log("Submitting form")
    let url = "/classes/course/session/" + session_id + "/react/" + react_num;
    fetch(url, {method: "POST"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .catch(handleError); 
}

function singleFormResults(form) {
    summary = {"Yes": 0, "Maybe": 0, "No": 0}
    keys = {0: "Yes", 1: "Maybe", 2: "No"}
    responses = form["responses"]
    for (r = responses.length - 1; r >= 0; r--) {
        // console.log(responses[r])
        summary[keys[responses[r]["form_responses"]]] += 1
    }

    return {"summary": summary,"keys": keys}
}


// Display results to the form
function displayFormResults(form) {
    console.log(">>> DISPLAYING FORMS")
    forms_html = document.getElementById("formsBox");
    document.getElementById("formsBox").innerHTML = ""; // Clearing all the content in the div
    console.log("YIP YOP")
    summary = singleFormResults(form)["summary"]
    forms_html.innerHTML = "<p><b>Summary - " + form["form_question"] +
        "</b><ul><li>Yes: " + summary["Yes"] + 
        "</li><li>Maybe: " +  summary["Maybe"] + 
        "</li><li>No: " +  summary["No"] + "</li></ul></p>"
}

function displayFormResultsAll(forms) {
    console.log('Updating individual form data divs')
    for (var key in forms) {
        results = singleFormResults(forms[key])
        summary = results["summary"]
        keys = results["keys"]

        var summary_div = document.getElementById("summary" + key)
        summary_div.innerHTML = ""
        summary_div.innerHTML = ('<p class="editedSummary"><b>Summary</b><ul><li>' +
            "Yes: " + summary["Yes"] + 
            "</li><li>Maybe: " + summary["Maybe"] +
            "</li><li>No: " + summary["No"] + "</li></ul></p>")
        
        var table_div = document.getElementById("table" + key)
        table_div.innerHTML = ""
        response_list = forms[key]["responses"]
        // console.log("RESPONSE LIST: " + response_list)
        for (r=response_list.length - 1; r >= 0; r--) {
            console.log("This response: " + response_list[r])
            table_div.innerHTML += ("<tr><td>" + response_list[r]["student_id"] + "</td><td>" +
                keys[response_list[r]["form_responses"]] + "</td><td>" +
                moment(response_list[r]["timestamp"]).format('hh:mm A') + "</td></tr>")
        }
    }
}


// function displayFormResultsAll(forms) {
//     forms_html2 = document.getElementById("formsBox2");
//     console.log("HELLO??")
//     // document.getElementById("formsBox2").innerHTML = ""; // Clearing all the content in the div
//     for (f=forms.length - 1; f >= 0; f--) {
//         // forms_html2.innerHTML += ('<div class="singleFormHolder">')
//         form_question = forms[f]["form_question"] // getting the form question, teacher, timestamp
//         form_teacher = forms[f]["teacher_id"]
//         form_timestamp = forms[f]["timestamp"]
//         responses_list = forms[f]["responses"] // responses list from the json file
//         // forms_html2.innerHTML += ('<h2>' + form_question + '</h2><h3>' + form_teacher + '</h3><h4>' + moment(form_timestamp).format('MMMM Do YYYY, h:mm a') + '</h4>')
//         forms_html2.innerHTML += ('<h2>' + form_question + '</h2><h4>' + moment(form_timestamp).format('MMMM Do YYYY, h:mm a') + '</h4>')
//         forms_html2.innerHTML += ('<div class="chartHolder" style="width: 500px;"><canvas id="chart' + f +  '" width="400" height="300"></canvas>')
//         response_counts = [0, 0, 0]
//         for (r = responses_list.length - 1; r >=0; r--) { // going through responses to get the student id and their responses
//             user_responder = responses_list[r]["student_id"]
//             response_user = responses_list[r]["form_responses"]            
//             timestamp_response = responses_list[r]["form_responses"]    
//             response_counts[response_user] += 1;
//             if (response_user == 0) {
//                 response_user = "Yes"
//             } else if (response_user == 1) {
//                 response_user = "Maybe"
//             } else if (response_user == 2){
//                 response_user = "No"
//             }   
//             forms_html2.innerHTML += ('<p>' +  user_responder + ' | ' + response_user + ' | ' + moment(timestamp_response).format('hh:mm a') + '</p>')
//         }

//         forms_html2.innerHTML += ("<p><b>Data Summary</b>Yes: " + response_counts[0] + "\nMaybe: " + response_counts[1] + "\nNo: " + response_counts[2]);
//         console.log(form_question + " " + response_counts.join(', '));
//         console.log("chart" + f);

//         // form_canvas = document.getElementById('chart' + form_timestamp).getContext('2d');
//         // console.log(form_canvas)

//         // document.getElementById('chart' + form_timestamp).innerHTML = (myChart)
//         forms_html2.innerHTML += ('</div>')
//     }
// }

function displayReactions(reactions) {
    // First have to delete all the existing reactions on the page
    reaction_html = document.getElementById("reactionResults")
    document.getElementById("reactionResults").innerHTML = ""; // Clearing all the content in the div 
    console.log("Testing")
    var reactions_counter = 0;
    var r_for;
    for (r_for = reactions.length - 1; r_for >= 0; r_for--) { // Gets the last five reactions
        console.log("HELLO HERE", reactions.length);
        reactions_counter++;
        if (reactions_counter > 5) {
            break; // Breaks out of the for loop
        }
        console.log("reactions: " + reactions[r_for]["emotions"]);
        console.log("user ID: " + reactions[r_for]["user_id"]);
        var user_reaction = reactions[r_for]["emotions"];
        var username = reactions[r_for]["user_id"];
        var emotions_timestamp = reactions[r_for]["emotions_timestamp"];
        if (user_reaction == 0) { // Determining what to print out based on the reaction number
            user_reaction = "<img class = 'makeSmaller' src='../../../../static/images/HappyShadow.png'>"
        } else if (user_reaction == 1) {
            user_reaction = "<img class = 'makeSmaller' src='../../../../static/images/MehShadow.png'>"
        } else {
            user_reaction = "<img class = 'makeSmaller' src='../../../../static/images/SadShadow2.png'>"
        }
        reaction_html.innerHTML += ('<div class = "userReactionView">' + '<div><p>' + moment(emotions_timestamp).format('hh:mm a') +  "<p>" + username + '</p></div><div>' + user_reaction + '</div>'); // Adding the new info to the div
    } 
}


// How to display the speeds
function displaySpeeds(speeds) {
    speed_html = document.getElementById("speedResults");
    visual_html = document.getElementById("speedVisual");
    var image = ""
    // Increment bunnies and turtles by their speed number
    // Whichever has more, go through that number and print out either bunnies or turtles
    document.getElementById("speedResults").innerHTML = ""; // Clears everything in the div first
    //document.getElementById("speedVisual").innerHTML = ""; // Clears everything in the div first 
    console.log("Testing");
    var speeds_counter = 0;
    var s_for;
    for (s_for = speeds.length - 1; s_for >= 0; s_for--) { // Going backwards through the json list of speeds to only get 5 of them
        speeds_counter++;
        if (speeds_counter > 5) {
            break; // Break out of the loop once 5 speeds have been grabbed
        }
        console.log("speed: " + speeds[s_for]["speed"]);
        console.log("user ID: " + speeds[s_for]["user_id"]);
        var user_speed = speeds[s_for]["speed"];
        var username = speeds[s_for]["user_id"];
        var speed_timestamp = speeds[s_for]["speed_timestamp"];
        if (user_speed == 6) { // Determining what string to print out depending on the number of the speed
            user_speed = "<img class = 'makeSmaller' src='../../../../static/images/Bunny.gif'>"; 
        } else {
            user_speed = "<img class = 'makeSmaller' src='../../../../static/images/Turtle.gif'>";
        }
        speed_html.innerHTML += ('<div class = "userReactionView">' + '<div class = "speedText"><p>' + moment(speed_timestamp).format('hh:mm a') +  "</p><p>" + username + "</p></div><div>" + user_speed + '</div>'); // Adds the info to the speedResults div    
    //visual_html.innerHTML += (image); // Adds the info to the speedResults div
    }
}

// How to display the calculated speed number
function displayCalculatedSpeed(data) {
    console.log("SPEED NUM");
    let visuals_slow = document.getElementsByClassName("visual_slow");
    let visuals_fast = document.getElementsByClassName("visual_fast");
    let visuals_all = document.getElementsByClassName("all");
    document.getElementById("speedVisual").innerHTML = ""; // Clears everything in the div previously
    for (let i = 0; i < 10; i++) { // Clears all the divs
        visuals_all[i].style.display = "none";
    }
    let speed_num = data;
    console.log(speed_num);
    speed_html = document.getElementById("paceTitle");
    speed_html.innerHTML = "" // Clears everything in the div
    //speed_html.innerHTML += ('<p>' + speed_num + '</p>'); // Adds the speed num to the div
    if (speed_num > 5) {
        speed_html.innerHTML += ('<h2>Speed Up</h2>');
    } else if (speed_num == 0) {
        speed_html.innerHTML += ('<h2>Good Pace!</h2>');
        speed_html.innerHTML += ("<img class = 'makeSmaller' src='../../../../static/images/GoodPace.gif'>");
    } else {
        speed_html.innerHTML += ('<h2>Slow Down</h2>');
    }
    //let visualHolder = document.getElementById("visualHolder");
    if (speed_num <= 5) {    
        for (let i = 0; i < speed_num; i++) {
            visuals_slow[i].style.display = "block";
        }
    } else if (speed_num > 5) {
        var vf = 0;
        for (let k = 5; k < speed_num; k++) {
            visuals_fast[vf].style.display = "block";
            vf++;
        }
    }
    
}


// Display the attendance
function displayAttendance(attendance) {
    console.log("Display Attendance");
    present_html = document.getElementById("present"); // Grabs the HTML div with the ID present
    absent_html = document.getElementById("absent");
    document.getElementById("present").innerHTML = ""; // Clears everything in the present div first
    document.getElementById("absent").innerHTML = ""; // Clears everything in the absent div first
    console.log("Attendance TESTING")
    console.log("Present Students: ")
    for (let a in attendance[0]["Present"]) {
        console.log(attendance[0]["Present"][a]);
        present_student = attendance[0]["Present"][a];
        present_html.innerHTML += ("<p>" + present_student + "</p>"); // Adding content to the present div
    }
    console.log("Absent Students: ")
    for (let a in attendance[1]["Absent"]) {
        console.log(attendance[1]["Absent"][a]);
        absent_student = attendance[1]["Absent"][a];
        absent_html.innerHTML += ("<p>" + absent_student + "</p>"); // Adding the content to the absent div
    }
}

function initTeacher(course_id, session_id, course_status) { // Course ID, session ID, and course status are all passed in through the rooms html page
    console.log("Called INIT Teacher", "Previous course status", course_status);
    fetchSessionInfoTeacher(course_id, session_id, course_status);
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("Update");
        fetchSessionInfoTeacher(course_id, session_id, course_status);
    }, 5000) // The fetchSessionInfo function will be called every 5 seconds  
}

// Have separate functions: initTeacher and initStudent
function initStudent(course_id, session_id, course_status) {
    console.log("Called INIT Student");
    fetchSessionInfoStudent(course_id, session_id, course_status);
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("Update");
        fetchSessionInfoStudent(course_id, session_id, course_status);
    }, 5000) 
}

// initFormsAll
function initFormsAll(course_id, session_id, course_status) {
    console.log("Called INIT Forms");
    // fetchSessionFormsInfo(course_id, session_id, course_status);
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("Update");
        fetchSessionFormsInfo(course_id, session_id, course_status);
    }, 5000) 
}

// function for manage class
function initManage(course_id) {
    console.log("Called INIT Forms");
    fetchCourseInfo(course_id);
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("Update");
        fetchCourseInfo(course_id);
    }, 5000) 
}

function pastInfo(course_id, session_id, course_status) {
    console.log("Called PAST INFO");
    fetchPastSessionInfo(course_id, session_id, course_status);
}

// Open a new page on which the teacher can download the report
function redirectToDownloadPage(session_id) {
    console.log("Opening DOWNLOAD Page")
    let url = "/classes/course/session/" + session_id + "/report"
    window.open(url)
}

// //download the pdf using jsPDF
// function create_and_save_pdf(course_name, start_time, end_time) {
//     pdf = new jsPDF('p', 'pt', 'letter')
//     let url = "/classes/course/session/" + session_id + "/report"
//     html_obj = fetch(url, {method: "GET"})
//     pdf.addHTML(html_obj, function () {
//         pdf.save('Test.pdf')
//     })
// }