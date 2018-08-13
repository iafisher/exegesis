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


function insertRow(lineno, element) {
    let commentRow = document.createElement("tr");
    commentRow.classList.add("comment-row");
    commentRow.appendChild(document.createElement("td"));
    let tableData = document.createElement("td");
    tableData.appendChild(element);
    commentRow.appendChild(tableData);
    insertAfter(lineno, commentRow);
}


function removeRow(lineno) {
    let commentRow = document.getElementById("line-" + lineno).nextSibling;
    commentRow.remove();
}


function saveCommentToDatabase(lineno, text) {
    postData("/api/update", { text: text, lineno: lineno });
}


function deleteCommentFromDatabase(lineno) {
    postData("/api/delete", { lineno: lineno });
}
