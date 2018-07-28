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
            insertAfter(commentFactory(""), item.parentNode);
        });
    }

    console.log("Listeners attached");
}

function commentFactory(text) {
    let textarea = document.createElement("textarea");
    let tableData = document.createElement("td");
    let tableRow = document.createElement("tr");

    textarea.classList.add("comment");
    textarea.value = text;

    let closeButton = buttonFactory("Close", () => {
        tableRow.remove();
    })

    let saveButton = buttonFactory("Save", () => {
        let p = document.createElement("p");
        p.classList.add("comment");
        p.innerHTML = textarea.value;

        // Remove all children of the table row.
        while (tableRow.firstChild) {
            tableRow.removeChild(tableRow.firstChild);
        }

        let deleteButton = buttonFactory("Delete", () => {
            tableRow.remove();
        });

        let editButton = buttonFactory("Edit", () => {
            let contents = p.innerHTML;

            insertAfter(commentFactory(contents), tableRow);
            tableRow.remove();
        });

        tableRow.appendChild(document.createElement("td"));
        tableRow.appendChild(p);
        tableRow.appendChild(deleteButton);
        tableRow.appendChild(editButton);
    });

    tableRow.appendChild(document.createElement("td"));
    tableRow.appendChild(tableData);
    tableData.appendChild(textarea);
    tableData.appendChild(closeButton);
    tableData.appendChild(saveButton);

    return tableRow;
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
