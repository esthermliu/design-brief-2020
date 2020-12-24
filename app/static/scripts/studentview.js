console.log("hello")

fetchStatus(); // Refreshes the page whenever class ends or starts

// Finds the status of the course when it is first activated/started
function fetchStatus() {
    let room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/course_status";
    console.log("FIRST STATUS");

    fetch(url, {method: "GET"})
        .then(checkStatus)
        .then(response => response.json())
        .then(activeFirst) // Refer to the activeFirst method below
        .catch(handleErrorStatus);
}

function handleErrorStatus() {
    console.log("ERROR");
    setInterval(function() {
        fetchStatus();
    }, 5000)
}

// Function that returns the original status of that course
function activeFirst(status) {
    let activeNum = 0;
    if (status.length == 0) {
        console.log("YEPAKJLAKJFL lkdsjf")
        activeNum = 0;
        console.log(activeNum)
    } else {
        activeNum = status[0]["status"]; // Sorting through status (which is the json file) to find the "status" field
    }                                    // Set activeNum to the appropriate value int he json
    console.log("Active Num:"); 
    console.log(activeNum);
    refetchStatus(activeNum); // Active num represents the original status of the course, calling refetchStatus and inputting this number into the function
}

//var firstNum = fetchStatus();

function refetchStatus(previousStatus) { // previousStatus is the original number representing the course's first status (equal to activeNum)
    const room_id = getRoomId();
    const url = "/classes/rooms/" + room_id + "/course_status";
    let redirect = "/classes/rooms/" + room_id;
    console.log("RECHECKING STATUS");

    function refreshPage(currentNumber) { // currentNumber is the number that represents the course's current status, this number is taken from the json file 
        console.log("LAKJLF");
        console.log("Previous status:");
        console.log(previousStatus);
        if (previousStatus != currentNumber) {
            console.log("UNEQUAL");
            window.location.assign(redirect);
        } else {
            console.log("EQUAL")
        }
        // Check currentNum with the firstNum
        // If they are different, refresh the page
    }

    setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("rechecking")
        fetch(url, {method: "GET"})
        .then(checkStatus)
        .then(response => response.json())
        .then(currentStatus)
        .then(refreshPage) // Calls the refreshPage function above and enters the current status number as the parameter
        .catch(handleError);
    }, 5000) 

}

function currentStatus(status) {
    console.log("WHATKJS")
    for (let s in status) {
        console.log(status[s]) 
    }
    console.log("WHATLKJJlkj")
    var currentNum = status[0]["status"];
    console.log("Current Num:");
    console.log(currentNum);
    return currentNum;
    // Return the current status number
}

function init() {
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        getPercentage();  // This is calling the function updateTherm1 and passes in the #yipyip id, which refers to a button in rooms html
        console.log("Update");
        fetchReactions();
        fetchSpeeds();
        fetchAttendance();
        fetchCalculatedSpeed();
    }, 5000) // The updateTherm1 function will be called every 5 seconds, therefore changing the value of the const interval
}

function getPercentage() {
    let room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/percent"; // Setting url to the url of the page with the percentage value ALERT: MAKE ROOM_ID DYNAMIC
    // let params = new FormData(); // Creating a new FormData object, which allows you to send form data
    // params.append("react", 1); // Inputting a value for the field react, gets this value from the getReact method which will return a number based on reaction ALERT: Change 1 here
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then(displayData) // Calls the displayData function, which will update the thermometer visually
        .catch(handleError); // Calls the handleError function which will send an error message to the console
}

function checkStatus(response) {
    if (!response.ok) { // If the response has caused an error
        throw Error("Error in request: " + response.statusText); // Throw the error and print the description of the text 
    }
    return response; // If it was successful, it will return the response's text
}

function displayData(data) { 
    console.log(data); // shows the percent number in the console, the data is the percentage, e.g. 50 or 33.333
    updateThermometer(data);// Calls the updateThermometer function, which updates the thermometer's height 
}

function handleError() {
    console.log("ERROR");
}

function updateThermometer(temp) {
    thermometer = document.getElementsByClassName("thermometer");
    console.log("Thermometer" + thermometer[0])
    console.log("Temperature: " + temp)
    thermometer[0].style.height = temp + "%";
}

function getRoomId() {
    idHolder = document.getElementById("yipyip") // Yipyip button has the course ID in its value
    console.log(idHolder)
    value = idHolder.value
    console.log("Room ID: " + value)
    return value // Returns the room ID
}

init(); // Calling the init() function

// Page won't refresh when user reacts
function submitForm() { // For the happy reaction
    console.log("clicked");
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/good"; 
    console.log(url)
    fetch(url, {method: "POST"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .catch(handleError); 
}

function submitFormOk() { // For the ok reaction
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/okay";
    fetch(url, {method: "POST"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .catch(handleError); 
}

function submitFormBad() { // For the bad reaction
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/bad";
    fetch(url, {method: "POST"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .catch(handleError); 
}

function fasterForm() { // For the faster request
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/fast";
    fetch(url, {method: "POST"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .catch(handleError); 
}

function slowerForm() { // For the slower request
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/slow";
    fetch(url, {method: "POST"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .catch(handleError); 
}

// First create a page that only holds the reactions
// Fetch the json from there

function fetchReactions() {
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/reactions_only";
    console.log("Fetched");
    fetch(url, {method: "GET"})
        .then(checkStatus)
        .then(response => response.json()) // Get all of the reactions
        .then(displayReactions) 
        .catch(handleError);
}

//fetchReactions()

function displayReactions(reactions) {
    // First have to delete all the existing reactions on the page
    // console.log("REACTIONS") // Testing whether this works in console 
    // console.log(reactions[0]["reactions_id"]);
    // console.log(reactions[0]["user_id"]);
    // console.log(reactions[0]["reactions"]);
    // console.log(reactions[0]["reactions_course_id"]);
    reaction_html = document.getElementById("reactionResults")
    document.getElementById("reactionResults").innerHTML = ""; // Clearing all the content in the div 
    console.log("Testing")
    for (let i in reactions) {
        console.log("reactions: " + reactions[i]["reactions"]);
        console.log("user ID: " + reactions[i]["user_id"]);
        var user_reaction = reactions[i]["reactions"];
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

// Fetch speeds from the json file
function fetchSpeeds() {
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/speeds_only";
    console.log("Speed fetched");
    fetch(url, {method: "GET"})
        .then(checkStatus)
        .then(response => response.json())
        .then(displaySpeeds)
        .catch(handleError);
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
        if (user_speed == 0) { // Determining what string to print out depending on the number of the speed
            user_speed = "Faster"; 
        } else {
            user_speed = "Slower";
        }
        speed_html.innerHTML += ('<p>' + user_speed + " | " + username + '</p>'); // Adds the info to the speedResults div    
    //visual_html.innerHTML += (image); // Adds the info to the speedResults div
    }
}

function fetchCalculatedSpeed() {
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/attendance_json";
    console.log("Attendance Fetched")
    fetch(url, {method: "GET"})
        .then(checkStatus)
        .then(response => response.json())
        .then(displayCalculatedSpeed)
        .catch(handleError);
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
    let speed_num = data[2]["speed"];
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



//fetchSpeeds();

// Fetch attendance from the json file
function fetchAttendance() {
    room_id = getRoomId();
    let url = "/classes/rooms/" + room_id + "/attendance_json";
    console.log("Attendance Fetched")
    fetch(url, {method: "GET"})
        .then(checkStatus)
        .then(response => response.json())
        .then(displayAttendance)
        .catch(handleError);
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

//fetchAttendance();

// function fetchStatus() {
//     room_id = getRoomId();
//     url = "/classes/rooms/" + room_id + "/course_status";
//     console.log("Refresh page");
//     fetch(url, {method: "GET"})
//         .then(checkStatus)
//         .then(response => response.json())
//         .then(refreshPage)
//         .catch(handleError);
// }

// function refreshPage(status) {
//     console.log("STATUS");
//     var isActive = False;
//     var newActive = False;
//     var activeList = [];
//     for (let s in status) {
//         console.log(status[s]["status"]);
//         s_num = status[s]["status"]; // 0 is inactive, 1 is active
//         if (s_num == 0) {
//             isActive = False; // The course is inactive
//         } else {
//             isActive = True; // Course is active
//         }
//         activeList[0] = isActive;
//     }
//     for (let s in status) {
//         console.log(status[s]["status"]);
//         s_num = status[s]["status"]; // 0 is inactive, 1 is active
//         if (s_num == 0) {
//             newActive = False; // Course is inactive
//         } else {
//             newActive = True; // Course is active
//         }
//     }
    
// }

// function fetchStatus() {
//     room_id = getRoomId();
//     url = "/classes/rooms/" + room_id + "/course_status";
//     console.log("FIRST STATUS");
//     fetch(url, {method: "GET"})
//         .then(checkStatus)
//         .then(response => response.json())
//         .then(activeFirst)
//         .catch(handleError);
// }

// function activeFirst(status) {
//     var activeNum = 0;
    
//     for (let s in status) {
//         s_num = status[s]["status"];
//         activeNum = s_num;
//     }
//     console.log("here");
//     console.log(activeNum);
//     return activeNum;
// }








// getRoomId()

// getPercentage()


// "use strict"; // Helps write cleaner code, e.g. prevents you from using undeclared variables

// (function() {
//     /** 
//      * Method for EventTarget
//      * Sets up a function that will be called when a specific event reaches its target (e.g. Element, Document, Window)
//      * @param {type, listener} - load is the type, init is the listener
//      * Load is the event type the function should listen for, load is fired when a resource has finished loading
//      * Init is the listener, which is the object that receives the notification when an event of the specified type occurs (in this case, it receives the notification when the resource has finished loading)
//      */ 
//     window.addEventListener("load", init) 

//     function init() { // This is the listener (it is a Javascript function in this case)
//         const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
//             updateTherm1("#yipyip")  // This is calling the function updateTherm1 and passes in the #yipyip id, which refers to a button in rooms html
//         }, 5000) // The updateTherm1 function will be called every 5 seconds, therefore changing the value of the const interval
        
//         qs("#yipyip").addEventListener("click", () => makePost("#yipyip")); // qs returns the first element that matches the selector
//         qs("#yopyop").addEventListener("click", () => makePost("#yipyip")); // click is fired when a button has been pressed and released on an element
//                                                                             // Arrow function shortens code, () => is the same as function()
//                                                                             // The function makePost is the listener, which means makePost will receive the notification when the button has been clicked
//                                                                             // The buttons with yipyip and yopyop as IDs are the selectors
//     }

//     function makePost(id) { // makePost receives the notification when the button has been clicked, #yipyip and #yopyop are passed in as id parameter
//         console.log("The button has been clicked");
//         let room_id = getRoomId(id); // Getting the room id from the function getRoomId
//         let url = "/classes/rooms/" + room_id; // Setting url to the url of the page with the percentage value
//         let params = new FormData(); // Creating a new FormData object, which allows you to send form data
//         params.append("react", getReact(id)); // Inputing a value for the field react, gets this value from the getReact method which will return a number based on reaction
//         fetch(url, {method: "POST", body: params})
//             .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
//             .then(response) // No json file
//             .then(displayData) // Calls the displayData function, which will update the thermometer visually
//             .catch(handleError); // Calls the handleError function which will send an error message to the console
//     } 

//     function updateTherm1(id) { // id being passed in will be #yipyip (refer to the init function)
//         let room_id = getRoomId(id); // Getting the room id form the function getRoomId
//         let param = "/classes/rooms/" + room_id + "/percent"; // What is the last part supposed to be?
//         fetch(param)
//             .then(checkStatus)
//             .then(response)
//             .then(displayData)
//             .catch(handleError);
//     }

//     function getRoomId(id) {
//         let val = qs(id).value; // val is set to the value of the object with the specified id. In this case, the value of yipyip is set to the room ID
//                                 // let declares a variable that can only be used within the block (have block scope, unlike var variables)
//         console.log(val); 
//         return val; // Returning the room ID taken from the buttons
//     }

//     function getReact(id) {
//         let val = qs(id).name; // Getting the name of the yipyip or yopyop button (which is either a 1 or 0)
//         console.log(val); 
//         return val; // Returning the name (1 or 0) of yipyip or yopyop
//     }

//     function displayData(data) { 
//         console.log(data);
//         updateThermometer(data) // Calls the updateThermometer function, which updates the thermometer's height
//     }

//     function updateThermometer(temp) { // Function that updates the thermometer visually
//         console.log("UPDATING " + temp.result);
//         qs(".thermometer").style.height = temp.result + "%"; // Sets the height of the thermometer div to the percentage result
//     }

//     /**
//      * Returns the first element matching the selector
//      * @param {string} selector - css query selector
//      * @returns {object} - DOM object associated with the selector 
//      */
//     function qs(selector) { 
//         console.log("hello")
//         return document.querySelector(selector);
//     }

//     /**
//      * Displays an error message in the console if an error has occurred anywhere
//      */
//     function handleError() {
//         console.log("ERROR");
//     }

//     /**
//      * returns the response's text if successful or throws an error otherwise
//      * @param {object} response - text to check for success or failure
//      * @returns {object} - successful response 
//      */
//     function checkStatus(response) {
//         if (!response.ok) { // If the response has caused an error
//             throw Error("Error in request: " + response.statusText); // Throw the error and print the description of the text 
//         }
//         return response; // If it was successful, it will return the response's text
//     }
// })

