"use strict";


// Call the onload function when the document is ready.
if (document.readyState === "complete" || (document.readyState !== "loading" &&
        !document.documentElement.doScroll)) {
    onload();
} else {
    document.addEventListener("DOMContentLoaded", onload);
}


function onload() {
    let button = document.getElementById("create-comment");
    button.onclick = () => {
        insertRow(0, renderNewForm(0));
    };
}


function insertRow(lineno, element) {
    document.getElementById("comment-div").appendChild(element);
    let button = document.getElementById("create-comment");
    button.style.display = "none";
}


function removeRow(lineno) {
    document.getElementById("comment-div").innerHTML = "";
    let button = document.getElementById("create-comment");
    button.style.display = "inline-block";
}


function saveCommentToDatabase(lineno, text) {
    // TODO
}


function  deleteCommentFromDatabase(lineno) {
    // TODO
}
