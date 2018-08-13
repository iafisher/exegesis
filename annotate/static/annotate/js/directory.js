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
    let div = document.getElementById("comment-div");
    div.appendChild(element);
    div.style.display = "block";

    let button = document.getElementById("create-comment");
    button.style.display = "none";
}


function removeRow(lineno) {
    let div = document.getElementById("comment-div");
    div.innerHTML = "";
    div.style.display = "none";

    let button = document.getElementById("create-comment");
    button.style.display = "inline-block";
}


function saveCommentToDatabase(lineno, text) {
    // TODO
}


function  deleteCommentFromDatabase(lineno) {
    // TODO
}
