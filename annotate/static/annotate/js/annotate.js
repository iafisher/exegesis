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
        trow.classList.add("code-row");
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
        renderComment(new Comment(comment.lineno, comment.user, comment.text,
            comment.created, comment.last_updated));
        insertCount++;
    }
}


function CommentChain(lineno, head) {
    return {
        lineno: lineno,
        comments: [head],
    };
}


function Comment(lineno, creator, text, created, lastUpdated) {
    return {
        lineno: lineno,
        creator: creator,
        text: text,
        created: created,
        lastUpdated: lastUpdated,
    };
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
            renderComment(new Comment(lineno, user, text, now, now));
        }
        commentRow.remove()
    });

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(tableData);
    tableData.appendChild(P("Commenting as: " + user));
    tableData.appendChild(textarea);
    tableData.appendChild(cancelButton);
    tableData.appendChild(saveButton);

    insertAfter(lineno, commentRow);
}


function renderComment(comment) {
    let commentRow = commentRowFactory();

    let deleteButton = buttonFactory("Delete", () => {
        if (window.confirm("Are you sure you want to delete this comment?")) {
            commentRow.remove();
            deleteCommentFromDatabase(comment.lineno);
        }
    });

    let editButton = buttonFactory("Edit", () => {
        commentRow.remove();
        renderEditForm(comment);
    });

    let hideButton = buttonFactory("Hide", () => {
        commentRow.remove();
        renderHiddenComment(comment);
    });

    let replyButton = buttonFactory("Reply", () => {
        renderNewForm(comment.lineno);
    });

    let converter = new showdown.Converter();
    let markdownP = document.createElement("p");
    markdownP.innerHTML = converter.makeHtml(comment.text);

    let td = document.createElement("td");
    td.appendChild(markdownP);
    td.appendChild(document.createElement("hr"));
    td.appendChild(P("Created on " + comment.created + " by " + comment.creator));
    if (comment.created !== comment.lastUpdated) {
        td.appendChild(P("Last updated on " + comment.lastUpdated));
    }
    if (user === comment.creator) {
        td.appendChild(deleteButton);
        td.appendChild(editButton);
    }
    td.appendChild(hideButton);
    td.appendChild(replyButton);
    commentRow.appendChild(td);

    insertAfter(comment.lineno, commentRow);
}


function renderHiddenComment(comment) {
    let commentRow = commentRowFactory();

    let showButton = buttonFactory("Show hidden comment", () => {
        commentRow.remove();
        renderComment(comment);
    });
    showButton.classList.add("show-button")

    let td = document.createElement("td");
    td.appendChild(showButton);
    commentRow.appendChild(td);

    insertAfter(comment.lineno, commentRow);
}


function renderEditForm(comment) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");
    textarea.value = comment.text;

    let commentRow = commentRowFactory();

    let cancelButton = buttonFactory("Cancel", () => {
        commentRow.remove();
        renderComment(comment);
    })

    let saveButton = buttonFactory("Save", () => {
        let newText = textarea.value.trim();
        if (newText.length > 0) {
            if (newText !== comment.text) {
                saveCommentToDatabase(comment.lineno, newText);
                comment.text = newText;
                comment.lastUpdated = formatDate(new Date());
                renderComment(comment);
            } else {
                renderComment(comment);
            }
        } else {
            deleteCommentFromDatabase(comment.lineno);
        }
        commentRow.remove();
    });

    let td = document.createElement("td");
    td.appendChild(P("Commenting as: " + user));
    td.appendChild(textarea);
    td.appendChild(cancelButton);
    td.appendChild(saveButton);
    commentRow.appendChild(td);

    insertAfter(comment.lineno, commentRow);
}


function commentRowFactory() {
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");
    commentRow.appendChild(document.createElement("td"));
    return commentRow;
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
    let referenceNode = document.getElementById("line-" + (lineno + 1));
    if (referenceNode !== null) {
        referenceNode.parentNode.insertBefore(newNode, referenceNode);
    } else {
        referenceNode = document.getElementById("line-" + lineno);
        referenceNode.parentNode.appendChild(newNode);
    }
}


/**
 * Format a Date object, e.g. 'Tuesday 07 August 2018, 10:36 AM'
 */
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
