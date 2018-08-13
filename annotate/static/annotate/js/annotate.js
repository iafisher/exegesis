/**
 * A library to create, edit, save, hide, show and delete comments.
 *
 * The library handles the creation of the comment elements and the actions
 * associated with their buttons. Users of the library are required to
 * implement the following functions:
 *
 *   insertRow(lineno, element): Insert an HTML element into the document.
 *   removeRow(lineno): Remove a row created by insertElement.
 *   saveCommentToDatabase(lineno, text): Save the comment to the database.
 *   deleteCommentFromDatabase(lineno): Delete the comment from the database.
 *
 * Author:  Ian Fisher (iafisher@protonmail.com)
 * Version: August 2018
 */

"use strict";


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
    hideButton.classList.add("hide-button");

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
