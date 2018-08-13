/**
 * The JavaScript code to insert, edit and delete comments.
 *
 * It's a bit of a mess, but unfortunately I think a clean framework like React
 * would be difficult to integrate with the syntax highlighting functionality
 * in an efficient way--I suspect that React would re-render the entire source
 * code table after every change, which would mean frequently drawing thousands
 * of lines for some large snippets.
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


let csrftoken = Cookies.get("csrftoken");
function onload() {
    fetch("/api/fetch?project=" + PROJECT + "&path=" + PATH, {
        method: "get",
        headers: {
            "X-CSRFToken": csrftoken,
        },
        credentials: "include",
    }).then(response => {
        response.json().then(onFetch);
    })
    .catch(error => {
        console.error('Fetch error: ', error);
    });
}


/**
 * When the page's data is retrieved, render the snippet as an HTML table with
 * line numbers, and insert pre-existing comments.
 */
function onFetch(data) {
    let highlighted = hljs.highlightAuto(data["text"]).value;
    let lines = highlighted.split("\n");

    let tbody = document.getElementById("table-body");
    for (let i = 0; i < lines.length; i++) {
        let trow = document.createElement("tr");
        trow.id = "line-" + (i + 1);
        trow.classList.add("code-row");
        trow.addEventListener("click", event => {
            let nextRow = event.target.parentNode.nextElementSibling;
            if (nextRow === null || !nextRow.classList.contains("comment-row")) {
                insertRow(i + 1, renderNewForm(i + 1));
            }
        });

        let td1 = document.createElement("td");
        td1.appendChild(document.createTextNode(i + 1));
        td1.classList.add("line-number");

        let td2 = document.createElement("td");
        td2.innerHTML = "<pre><code>" + lines[i] + "</code></pre>";
        td2.classList.add("code-line")

        trow.appendChild(td1);
        trow.appendChild(td2);
        tbody.appendChild(trow);
    }

    for (let comment of data["comments"]) {
        comment = new Comment(comment.lineno, comment.user, comment.text,
            comment.created, comment.last_updated);
        insertRow(comment.lineno, renderComment(comment));
    }
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


function insertRow(lineno, element) {
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");
    commentRow.appendChild(document.createElement("td"));
    let tableData = document.createElement("td");
    tableData.appendChild(element);
    commentRow.appendChild(tableData);
    insertAfter(lineno, commentRow);
}


function renderNewForm(lineno) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");

    let converter = new showdown.Converter({noHeaderId: true});
    let preview = document.createElement("div");
    preview.classList.add("preview");
    textarea.oninput = () => {
        preview.innerHTML = converter.makeHtml(textarea.value);
    };

    let cancelButton = buttonFactory("Cancel", () => {
        removeRow(lineno);
    })

    let saveButton = buttonFactory("Save", () => {
        let text = textarea.value.trim();
        removeRow(lineno);
        if (text.length > 0) {
            saveCommentToDatabase(lineno, text);
            let now = formatDate(new Date());
            let commentDiv = renderComment(new Comment(lineno, USER, text,
                now, now));
            insertRow(lineno, commentDiv);
        }
    });

    let commentDiv = document.createElement("div");
    commentDiv.appendChild(P("Commenting as: " + USER));
    commentDiv.appendChild(textarea);
    commentDiv.appendChild(preview);
    commentDiv.appendChild(cancelButton);
    commentDiv.appendChild(saveButton);
    return commentDiv;
}


function renderComment(comment) {
    let deleteButton = buttonFactory("Delete", () => {
        if (window.confirm("Are you sure you want to delete this comment?")) {
            removeRow(comment.lineno);
            deleteCommentFromDatabase(comment.lineno);
        }
    });

    let editButton = buttonFactory("Edit", () => {
        removeRow(comment.lineno);
        insertRow(comment.lineno, renderEditForm(comment));
    });

    let hideButton = buttonFactory("Hide", () => {
        removeRow(comment.lineno);
        insertRow(comment.lineno, renderHiddenComment(comment));
    });

    let converter = new showdown.Converter();
    let markdownP = document.createElement("p");
    markdownP.innerHTML = converter.makeHtml(comment.text);

    let commentDiv = document.createElement("div");
    commentDiv.appendChild(markdownP);
    commentDiv.appendChild(document.createElement("hr"));
    commentDiv.appendChild(P("Created on " + comment.created + " by "
        + comment.creator));

    if (comment.created !== comment.lastUpdated) {
        commentDiv.appendChild(P("Last updated on " + comment.lastUpdated));
    }
    if (USER === comment.creator) {
        commentDiv.appendChild(deleteButton);
        commentDiv.appendChild(editButton);
    }
    commentDiv.appendChild(hideButton);
    return commentDiv;
}


function removeRow(lineno) {
    let commentRow = document.getElementById("line-" + lineno).nextSibling;
    commentRow.remove();
}


function renderHiddenComment(comment) {
    let showButton = buttonFactory("Show hidden comment", () => {
        removeRow(comment.lineno);
        insertRow(comment.lineno, renderComment(comment));
    });
    showButton.classList.add("show-button")

    let commentDiv = document.createElement("div");
    commentDiv.appendChild(showButton);
    return commentDiv;
}


function renderEditForm(comment) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");
    textarea.value = comment.text;

    let cancelButton = buttonFactory("Cancel", () => {
        removeRow(comment.lineno);
        insertRow(comment.lineno, renderComment(comment));
    })

    let saveButton = buttonFactory("Save", () => {
        let newText = textarea.value.trim();
        removeRow(comment.lineno);
        if (newText.length > 0) {
            if (newText !== comment.text) {
                saveCommentToDatabase(comment.lineno, newText);
                comment.text = newText;
                comment.lastUpdated = formatDate(new Date());
            }
            insertRow(comment.lineno, renderComment(comment));
        } else {
            deleteCommentFromDatabase(comment.lineno);
        }
    });

    let commentDiv = document.createElement("div");
    commentDiv.appendChild(P("Commenting as: " + USER));
    commentDiv.appendChild(textarea);
    commentDiv.appendChild(cancelButton);
    commentDiv.appendChild(saveButton);
    return commentDiv;
}


function saveCommentToDatabase(lineno, text) {
    postData("/api/update", { text: text, lineno: lineno });
}


function deleteCommentFromDatabase(lineno) {
    postData("/api/delete", { lineno: lineno });
}


/**
 * Post the plain object `data` to the given URL.
 */
function postData(url, data) {
    // `PROJECT` and `PATH` are global variables defined in snippet.html.
    data.project = PROJECT;
    data.path = PATH;
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
