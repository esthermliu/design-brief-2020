// Fetches the course status on the unactivated html page to decide when to refresh the page
function fetchCourseStatus(course_id, status) {
    let url = "/classes/course/" + course_id + "/course_status_json";
    fetch(url, {method: "GET"})
        .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
        .then(response => response.json()) 
        .then((data) => compareStatus(status, data)) // Calls the compareStatus function, which will compare the previous status to the new status of the course
        .catch(handleError);
}

// Compares the previous status of the course to the new
function compareStatus(oldStatus, data) {
    newStatus = data["status"]
    if (oldStatus != newStatus) { // If the old status and new status are not the same
        console.log("SHOULD REFRESH THE PAGE", oldStatus, newStatus);
        location.reload(); // Then refresh the page
    }
}

function checkStatus(response) {
    if (!response.ok) { // If the response has caused an error
        throw Error("Error in request: " + response.statusText); // Throw the error and print the description of the text 
    }
    return response; // If it was successful, it will return the response's text
}

function handleError(err) {
    console.log("Ran into error:", err);
}

function init(course_id, course_status) {
    console.log("Called INIT", "Previous course status", course_status);
    const interval = setInterval(function() { // setInterval method calls a function or evaluates an expression at specified intervals
        console.log("Update");
        fetchCourseStatus(course_id, course_status);
    }, 5000) // The fetchCourseStatus function will be called every 5 seconds
}


