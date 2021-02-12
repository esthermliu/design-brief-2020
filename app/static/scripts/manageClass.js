function removeUser(username, user_id) {
    if (confirm("Are you sure you want to remove " + username + "?")) {
        console.log("Removing user: " + username)
        let url = "/classes/course/session/" + session_id + "/react/" + react_num;
        fetch(url, {method: "GET"})
            .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
            .catch(handleError); 
    }
}

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