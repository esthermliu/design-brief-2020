function divLink(course_id) {
    window.location = "/classes/course/" + course_id;
}

function divLinkSessions(course_id, session_id) {
    window.location = "/classes/course/" + course_id + "/previous_session_data/" + session_id;
}