function removeUser(username, user_id, course_id) {
    console.log('Remove user has been called with parameters: ' + username + ',' + user_id + ', ' + course_id)
    if (confirm("Are you sure you want to remove " + username + "?")) {
        console.log("Removing user: " + username)
        let url = "/classes/course/course/" + course_id + "/remove/" + user_id;
        fetch(url, {method: "POST"})
            .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
            .catch(handleError); 
    }
}