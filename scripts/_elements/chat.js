function createMessage(message, time, type, messageType, url) {
    let chat = document.getElementById("text-area");
    let div = document.createElement("div");
    chat.appendChild(div);

    let div2 = document.createElement("div");
    div.appendChild(div2);
    if (messageType == "text") {
        let p = document.createElement("p");
        p.className = "small mb-0";
        p.textContent = message;
        div2.appendChild(p);
    } else if (messageType == "url") {
        let a = document.createElement("a");
        a.className = "small mb-0";
        a.href = message;
        a.target = "_blank";
        a.textContent = "Open link";
        div2.appendChild(a);
        let br = document.createElement("br");
        div2.appendChild(br);
    } else if (messageType == "question") {
        let p = document.createElement("p");
        p.className = "small mb-0";
        let answer = message.split(";");
        p.textContent = answer[0];
        div2.appendChild(p);
        let p2 = document.createElement("p");
        p2.className = "small mb-0";
        p2.textContent = answer[1];
        div2.appendChild(p2);
        let p3 = document.createElement("p");
        p3.className = "small mb-0";
        p3.textContent = answer[2];
        div2.appendChild(p3);
    }
    let p2 = document.createElement("p");
    p2.className = "hour";
    p2.textContent = time;
    div2.appendChild(p2);

    if (type == "0") {
        div.className = "d-flex flex-row justify-content-start mb-4";
        div2.className = "p-3 ms-3 sender";
    } else {
        div.className = "d-flex flex-row justify-content-end mb-4";
        div2.className = "p-3 me-3 border receiver";
        let img = document.createElement("img");
        img.className = "avatar";
        img.src = url;
        div.appendChild(img);
    }
}

function createChat(sender, url) {
    let content = document.getElementById(sender);
    let myObJ = JSON.parse(content.textContent);
    //destroy old chat
    let chat = document.getElementById("text-area");
    chat.innerHTML = "";
    //create new chat
    let title = document.getElementById("title");
    title.textContent = myObJ.name;
    for (let i = 0; i < myObJ.messages.length; i++) {
        if (myObJ.messages[i].sender != sender) {
            createMessage(myObJ.messages[i].message, myObJ.messages[i].time, "0", myObJ.messages[i].type, url);
        } else {
            createMessage(myObJ.messages[i].message, myObJ.messages[i].time, "1", myObJ.messages[i].type, url);
        }
        sender = myObJ.messages[i].sender;
    }
}