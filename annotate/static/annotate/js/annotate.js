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
        trow.addEventListener("click", event => {
            let nextRow = event.target.parentNode.nextElementSibling;
            if (nextRow === null || !nextRow.classList.contains("comment-row")) {
                insertCommentForm(event.target.parentNode, "");
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
}


/**
 * Insert a comment form after `row`. The placeholder value of the textarea is
 * initialized to `text`.
 */
function insertCommentForm(row, text, created, lastUpdated) {
    let textarea = document.createElement("textarea");
    textarea.classList.add("comment");
    textarea.value = text;

    let tableData = document.createElement("td");
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");

    let cancelButton = buttonFactory("Cancel", () => {
        if (text.length > 0) {
            insertSavedComment(row, text, created, lastUpdated);
        }
        commentRow.remove();
    })

    let saveButton = buttonFactory("Save", () => {
        let text = textarea.value.trim();

        if (text.length > 0) {
            saveCommentToDatabase(row, textarea.value);
            insertSavedComment(row, textarea.value, created, lastUpdated);
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
    p2.appendChild(P("Created at " + created));
    if (created !== lastUpdated) {
        p2.appendChild(P("Last updated at " + lastUpdated));
    }

    let deleteButton = buttonFactory("Delete", () => {
        deleteCommentFromDatabase(row);
        commentRow.remove();
    });

    let editButton = buttonFactory("Edit", () => {
        insertCommentForm(row, p1.innerHTML, created, lastUpdated);
        commentRow.remove();
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

    insertAfter(commentRow, row);
}


function buttonFactory(label, clickhandler) {
    let button = document.createElement("button");
    button.innerHTML = label;
    button.addEventListener("click", clickhandler);
    return button;
}


function saveCommentToDatabase(row, text) {
    let lineno = parseInt(row.children[0].textContent);
    console.log(text, lineno);
    postData(path + "/update", { text: text, lineno: lineno });
}


function deleteCommentFromDatabase(row) {
    let lineno = parseInt(row.children[0].textContent);
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
        body: JSON.stringify(data),
        credentials: "include",
    })
    .catch(error => {
        console.error('Fetch error: ', error);
    });
}


function P(text) {
    let p = document.createElement("p");
    p.appendChild(document.createTextNode(text));
    return p;
}


/* Courtesy of https://stackoverflow.com/questions/4793604/ */
function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}


class RowManager {
    constructor(parentRow) {
        this.parentRow = parentRow;
        this.text = "";
    }

    renderNew() {

    }

    renderEdit() {

    }

    render() {

    }

    remove() {

    }

    save() {

    }
}
