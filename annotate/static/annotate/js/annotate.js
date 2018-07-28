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
    for (let comment of comments) {
        let row = document.querySelector("tr:nth-child(" + (comment.lineno + insertCount) + ")");
        insertSavedComment(row, comment.text);
        insertCount++;
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
function insertSavedComment(row, text) {
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let p = document.createElement("p");
    p.classList.add("comment");
    p.innerHTML = text;

    let deleteButton = buttonFactory("Delete", () => {
        deleteCommentFromDatabase(row);
        commentRow.remove();
    });

    let editButton = buttonFactory("Edit", () => {
        insertCommentForm(row, p.innerHTML);
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
