function removeUser(username, user_id) {
    if (confirm("Are you sure you want to remove " + username + "?")) {
        console.log("Removing user: " + username)
        let url = "/classes/course/session/" + session_id + "/react/" + react_num;
        fetch(url, {method: "GET"})
            .then(checkStatus) // Calls the checkStatus function, which checks whether the response is successful, throws error otherwise
            .catch(handleError); 
    }
}

