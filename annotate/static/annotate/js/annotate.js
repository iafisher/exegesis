/**
 * The JavaScript code to insert, edit and delete comments.
 *
 * It's a bit of a mess, but unfortunately I think a clean framework like React
 * would be difficult to integrate with the syntax highlighting library.
 *
 * Author:  Ian Fisher (iafisher@protonmail.com)
 * Version: August 2018
 */

"use strict";

// Call the onload function when the document is ready.
if (document.readyState === "complete" || (document.readyState !== "loading" &&
        !document.documentElement.doScroll)) {
    onload();
} else {
    document.addEventListener("DOMContentLoaded", onload);
}


function onload() {
    let highlighted = hljs.highlightAuto(document.getElementById("snippet").textContent).value;
    let lines = highlighted.split("\n");
    let table = document.createElement("table");
    let tbody = document.createElement("tbody");
    table.appendChild(tbody);
    for (let i = 0; i < lines.length; i++) {
        let trow = document.createElement("tr");
        trow.id = "line-" + (i + 1);
        trow.addEventListener("click", event => {
            let nextRow = event.target.parentNode.nextElementSibling;
            if (nextRow === null || !nextRow.classList.contains("comment-row")) {
                renderNewForm(i + 1);
            }
        });

        let td1 = document.createElement("td");
        td1.appendChild(document.createTextNode(i + 1));
        td1.classList.add("line-number");

        let td2 = document.createElement("td");
        td2.innerHTML = lines[i];
        td2.classList.add("code-line")

        trow.appendChild(td1);
        trow.appendChild(td2);
        tbody.appendChild(trow);
    }

    document.getElementById("snippet").innerHTML = "";
    document.getElementById("snippet").appendChild(table);

    let insertCount = 0;
    // comments is a global variable defined in an inline script in
    // snippet.html. Its value ultimately comes from the back-end database by
    // way of Django.
    //
    // Gross, I know.
    //
    // TODO: Replace this with an API call to the back-end.
    for (let comment of comments) {
        renderComment(comment.lineno, comment.user, comment.text,
            comment.created, comment.last_updated);
        insertCount++;
    }
}


function renderNewForm(lineno) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");

    let tableData = document.createElement("td");
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let cancelButton = buttonFactory("Cancel", () => {
        commentRow.remove();
    })

    let saveButton = buttonFactory("Save", () => {
        let text = textarea.value.trim();
        if (text.length > 0) {
            saveCommentToDatabase(lineno, text);
            let now = formatDate(new Date());
            renderComment(lineno, user, text, now, now);
        }
        commentRow.remove()
    });

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(tableData);
    tableData.appendChild(textarea);
    tableData.appendChild(cancelButton);
    tableData.appendChild(saveButton);

    insertAfter(lineno, commentRow);
}


function renderComment(lineno, creator, text, created, lastUpdated) {
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let p1 = document.createElement("p");
    p1.classList.add("comment");
    p1.appendChild(document.createTextNode(text));

    let p2 = document.createElement("p");
    p2.classList.add("comment");
    p2.appendChild(P("Created on " + created + " by " + creator));
    if (created !== lastUpdated) {
        p2.appendChild(P("Last updated on " + lastUpdated));
    }

    let deleteButton = buttonFactory("Delete", () => {
        commentRow.remove();
        deleteCommentFromDatabase(lineno);
    });

    let editButton = buttonFactory("Edit", () => {
        commentRow.remove();
        renderEditForm(lineno, creator, text, created, lastUpdated);
    });

    let pData = document.createElement("td");
    pData.classList.add("comment-data");
    pData.appendChild(p1);
    pData.appendChild(document.createElement("hr"));
    pData.appendChild(p2);
    pData.appendChild(deleteButton);
    pData.appendChild(editButton);

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(pData);

    insertAfter(lineno, commentRow);
}


function renderEditForm(lineno, creator, text, created, lastUpdated) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");
    textarea.value = text;

    let tableData = document.createElement("td");
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let cancelButton = buttonFactory("Cancel", () => {
        commentRow.remove();
        renderComment(lineno, creator, text, created, lastUpdated);
    })

    let saveButton = buttonFactory("Save", () => {
        let newText = textarea.value.trim();
        if (newText.length > 0) {
            if (newText !== text) {
                saveCommentToDatabase(lineno, newText);
                renderComment(lineno, creator, newText, created,
                    formatDate(new Date()));
            } else {
                renderComment(lineno, creator, newText, created, lastUpdated);
            }
        } else {
            deleteCommentFromDatabase(lineno);
        }
        commentRow.remove();
    });

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(tableData);
    tableData.appendChild(textarea);
    tableData.appendChild(cancelButton);
    tableData.appendChild(saveButton);

    insertAfter(lineno, commentRow);
}



function saveCommentToDatabase(lineno, text) {
    // `path` is a global variable defined in snippet.html.
    postData(path + "/update", { text: text, lineno: lineno });
}


function deleteCommentFromDatabase(lineno) {
    // `path` is a global variable defined in snippet.html.
    postData(path + "/delete", { lineno: lineno });
}


/**
 * Post the plain object `data` to the given URL.
 */
let csrftoken = Cookies.get("csrftoken");
function postData(url, data) {
    fetch(url, {
        method: "post",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data),
        credentials: "include",
    })
    // TODO: Catch non-200 responses, and display an error message.
    .catch(error => {
        console.error('Fetch error: ', error);
    });
}


/**
 * Create a new <p> element with the given text content.
 */
function P(text) {
    let p = document.createElement("p");
    p.appendChild(document.createTextNode(text));
    return p;
}


/**
 * Create a new <button> element with the given label and onclick event handler.
 */
function buttonFactory(label, clickhandler) {
    let button = document.createElement("button");
    button.innerHTML = label;
    button.addEventListener("click", clickhandler);
    return button;
}


/* Courtesy of https://stackoverflow.com/questions/4793604/ */
function insertAfter(lineno, newNode) {
    let referenceNode = document.getElementById("line-" + lineno);
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}


'Tuesday 07 August 2018, 10:36 AM'
function formatDate(date) {
    return dayNumberToName(date.getUTCDay()) + " " + date.getUTCDate() + " " +
        monthNumberToName(date.getUTCMonth()) + " " + date.getUTCFullYear() +
        ", " + pad(date.getUTCHours()) + ":" + pad(date.getUTCMinutes()) +
        " UTC";
}


function pad(number) {
    return number >= 10 ? "" + number : "0" + number;
}


const months = ["January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December"];
function monthNumberToName(month) {
    return months[month];
}


const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday"];
function dayNumberToName(day) {
    return days[day];
}
