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
    // Wait a short amount of time for line-number initialization to finish.
    setTimeout(attachListeners, 500);
}


function attachListeners() {
    let lineNumbers = document.querySelectorAll(".hljs-ln-code");

    for (let item of lineNumbers) {
        item.addEventListener("click", () => {
            insertCommentForm(item.parentNode, "");
        });
    }

    // comments is a global variable defined in an inline script in snippet.html
    // Its value ultimately comes from the back-end database by way of Django.
    for (let comment of comments) {
        let row = document.querySelector("tr:nth-child(" + comment.lineno + ")");
        insertSavedComment(row, comment.text);
    }
}


/**
 * Insert a comment form after `row`. The placeholder value of the textarea is
 * initialized to `text`.
 */
function insertCommentForm(row, text) {
    let textarea = document.createElement("textarea");
    let tableData = document.createElement("td");
    let commentRow = document.createElement("tr");

    textarea.classList.add("comment");
    textarea.value = text;

    let cancelButton = buttonFactory("Cancel", () => {
        commentRow.remove();
    })

    let saveButton = buttonFactory("Save", () => {
        insertSavedComment(commentRow, textarea.value);
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
function insertSavedComment(row, text) {
    let commentRow = document.createElement("tr");
    let p = document.createElement("p");
    p.classList.add("comment");
    p.innerHTML = text;

    let deleteButton = buttonFactory("Delete", () => {
        commentRow.remove();
    });

    let editButton = buttonFactory("Edit", () => {
        insertCommentForm(commentRow, p.innerHTML);
        commentRow.remove();
    });

    commentRow.appendChild(document.createElement("td"));
    commentRow.appendChild(p);
    commentRow.appendChild(deleteButton);
    commentRow.appendChild(editButton);

    insertAfter(commentRow, row);
}


function buttonFactory(label, clickhandler) {
    let button = document.createElement("button");
    button.innerHTML = label;
    button.addEventListener("click", clickhandler);
    return button;
}


/* Courtesy of https://stackoverflow.com/questions/4793604/ */
function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
