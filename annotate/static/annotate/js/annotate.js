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

hljs.initHighlightingOnLoad();
hljs.initLineNumbersOnLoad();


function onload() {
    // We want to pass the timeout ID to the interval function, so it can
    // detach itself as soon as it succeeds in attaching the listener. But
    // we don't get the timeout ID until setInterval returns, so we have to use
    // this hack.
    let data = {};
    let timeoutID = setInterval(tryToAttachListeners, 100, data);
    data.timeoutID = timeoutID;
}


function tryToAttachListeners(data) {
    let lineNumbers = document.querySelectorAll(".hljs-ln-code");
    if (lineNumbers.length !== 0) {
        for (let item of lineNumbers) {
            item.addEventListener("click", () => {
                let nextRow = item.parentNode.nextElementSibling;
                if (nextRow === null || !nextRow.classList.contains("comment-row")) {
                    insertCommentForm(item.parentNode, "");
                }
            });
        }

        let insertCount = 0;
        // comments is a global variable defined in an inline script in
        // projectfile.html. Its value ultimately comes from the back-end database
        // by way of Django.
        //
        // Gross, I know.
        for (let comment of comments) {
            let row = document.querySelector("tr:nth-child(" + (comment.lineno + insertCount) + ")");
            insertSavedComment(row, comment.text, comment.created,
                comment.last_updated);
            insertCount++;
        }

        // Remove this interval function.
        window.clearInterval(data.timeoutID);
    }
}


/**
 * Insert a comment form after `row`. The placeholder value of the textarea is
 * initialized to `text`.
 */
function insertCommentForm(row, text) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");
    textarea.value = text;

    let tableData = document.createElement("td");
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let cancelButton = buttonFactory("Cancel", () => {
        if (text.length > 0) {
            insertSavedComment(row, text);
        }
        commentRow.remove();
    })

    let saveButton = buttonFactory("Save", () => {
        let text = textarea.value.trim();

        if (text.length > 0) {
            saveCommentToDatabase(row, textarea.value);
            insertSavedComment(row, textarea.value);
        } else {
            deleteCommentFromDatabase(row);
        }
        commentRow.remove();
    });

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(tableData);
    tableData.appendChild(textarea);
    tableData.appendChild(cancelButton);
    tableData.appendChild(saveButton);

    insertAfter(commentRow, row);
}


/**
 * Insert a comment after `row`.
 */
function insertSavedComment(row, text, created, lastUpdated) {
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let p1 = document.createElement("p");
    p1.classList.add("comment");
    p1.appendChild(document.createTextNode(text));

    let p2 = document.createElement("p");
    p2.classList.add("comment");
    let timestampText;
    if (created === lastUpdated) {
        timestampText = "Created at " + created;
    } else {
        timestampText = "Created at " + created + ", last updated at "
            + lastUpdated;
    }
    p2.appendChild(document.createTextNode(timestampText));

    let deleteButton = buttonFactory("Delete", () => {
        deleteCommentFromDatabase(row);
        commentRow.remove();
    });

    let editButton = buttonFactory("Edit", () => {
        insertCommentForm(row, p1.innerHTML);
        commentRow.remove();
    });

    let pData = document.createElement("td");
    pData.classList.add("comment-data");
    pData.appendChild(p1);
    pData.appendChild(p2);
    pData.appendChild(deleteButton);
    pData.appendChild(editButton);

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(pData);

    insertAfter(commentRow, row);
}


function buttonFactory(label, clickhandler) {
    let button = document.createElement("button");
    button.innerHTML = label;
    button.addEventListener("click", clickhandler);
    return button;
}


function saveCommentToDatabase(row, text) {
    let lineno = parseInt(row.children[0].children[0].getAttribute('data-line-number'));
    postData(path + "/update", { text: text, lineno: lineno });
}


function deleteCommentFromDatabase(row) {
    let lineno = parseInt(row.children[0].children[0].getAttribute('data-line-number'));
    postData(path + "/delete", { lineno: lineno });
}


let csrftoken = Cookies.get("csrftoken");
function postData(path, data) {
    fetch(path, {
        method: "post",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .catch(error => {
        console.error('Fetch error: ', error);
    });
}


/* Courtesy of https://stackoverflow.com/questions/4793604/ */
function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
