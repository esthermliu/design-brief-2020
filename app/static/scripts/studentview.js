// Fetches all the session info
function fetchSessionInfo(course_id, session_id, status) {
    let url = "/classes/course/session/" + session_id + "/session_json";
    console.log("HELLO")
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => displayAll(status, data)) // Calls the displayData function, which will update the thermometer visually
        .catch(handleError);
}

function displayAll(status, data) {
    checkIfShouldRefresh(status, data["course_status"])
    displayPercentage(data["percentage"]); // Display percentage on the thermometer
    console.log(data["percentage"]);
    displayReactions(data["reactions"]); // Display emotions
    displaySpeeds(data["speeds"]); // Display speeds
    displayCalculatedSpeed(data["speed_num"]); // Display the calculated speed number
    displayAttendance(data["attendance"]); // Display the attendance
}

function checkIfShouldRefresh(oldStatus, newStatus) {
    if (oldStatus != newStatus) {
        console.log("SHOULD REFRESH THE PAGE", oldStatus, newStatus);
        location.reload()
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

function handleError(err) {
    console.log("Ran into error:", err);
}

function updateThermometer(temp) {
    thermometer = document.getElementsByClassName("thermometer"); // Returns an array of elements with that class name
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

function displayReactions(reactions) {
    // First have to delete all the existing reactions on the page
    reaction_html = document.getElementById("reactionResults")
    document.getElementById("reactionResults").innerHTML = ""; // Clearing all the content in the div 
    console.log("Testing")
    for (let i in reactions) {
        console.log("reactions: " + reactions[i]["emotions"]);
        console.log("user ID: " + reactions[i]["user_id"]);
        var user_reaction = reactions[i]["emotions"];
        var username = reactions[i]["user_id"];
        if (user_reaction == 0) { // Determining what to print out based on the reaction number
            user_reaction = "Good"
        } else if (user_reaction == 1) {
            user_reaction = "Okay"
        } else {
            user_reaction = "Bad"
        }
        reaction_html.innerHTML += ('<p>' + user_reaction + " | " + username + '</p>'); // Adding the new info to the div
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
    for (let i in speeds) {
        console.log("speed: " + speeds[i]["speed"]);
        console.log("user ID: " + speeds[i]["user_id"]);
        var user_speed = speeds[i]["speed"];
        var username = speeds[i]["user_id"];
        if (user_speed == 6) { // Determining what string to print out depending on the number of the speed
            user_speed = "Faster"; 
        } else {
            user_speed = "Slower";
        }
        speed_html.innerHTML += ('<p>' + user_speed + " | " + username + '</p>'); // Adds the info to the speedResults div    
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
    speed_html = document.getElementById("speedVisual");
    speed_html.innerHTML += ('<p>' + speed_num + '</p>'); // Adds the speed num to the div
    //let visualHolder = document.getElementById("visualHolder");
    if (speed_num == 100) {

    }
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

function init(course_id, session_id, course_status) {
    console.log("Called INIT", "Previous course status", course_status);
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("Update");
        fetchSessionInfo(course_id, session_id, course_status);
    }, 5000) // The updateTherm1 function will be called every 5 seconds
}
