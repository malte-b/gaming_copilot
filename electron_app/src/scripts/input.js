const messagesContainer = document.querySelector(".messages-container");

/**
 * Handling the case when user submits the form either by clicking on search button
 * or pressing enter key
 */
document
    .getElementById("input-form")
    .addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(event.target);
        const user_message = formData.get("query");
        if (!user_message) {
            // @ TODO: Show an alert
            return;
        }

        appendMessage(user_message, "user-message")
        startThinking()

        const source = new SSE(
            "http://127.0.0.1:5000/generate-langchain-response-endpoint",
            {
                payload: JSON.stringify({ user_message }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: "POST",
            }
        );

        source.addEventListener("message", function (event) {
            stopThinking()

            const payload = JSON.parse(event.data.replace('---END OF EVENT---', ''))


            if (payload.type === "onText") {
                appendMessage(payload.content, "ai-message")
            }

            if (payload.type === "onImageUrl") {
                appendMessage(payload.content, "image-url")
            }
        });

        event.target.reset();
    });

function appendMessage(message, type) {
    // Creating outer div of message
    const messageWrapperDiv = document.createElement("div");
    messageWrapperDiv.classList.add("message-wrapper");

    // Flex reverse if message is by user
    if (type === "user-message") {
        messageWrapperDiv.classList.add("reverse");
    }

    // Creating actual message `p`
    if (type === 'image-url') {
        const messageImg = document.createElement('img')
        messageImg.src = message

        // Appending message image to div
        messageWrapperDiv.appendChild(messageImg);
    } else {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        // Transforming markdown to html
        const classMap = {
            ul: 'ui inline-list',
            ol: 'ui inline-list'
        }

        const bindings = Object.keys(classMap)
            .map(key => ({
                type: 'output',
                regex: new RegExp(`<${key}(.*)>`, 'g'),
                replace: `<${key} class="${classMap[key]}" $1>`
            }));


        const converter = new showdown.Converter({ extensions: [...bindings] })
        const html = converter.makeHtml(message);
        messageDiv.innerHTML = html;

        // Appending message `p` to div
        messageWrapperDiv.appendChild(messageDiv);
    }

    // Apending div to our messages container
    messagesContainer.appendChild(messageWrapperDiv);
}

function startThinking() {
    const messageWrapperDiv = document.createElement("div");
    messageWrapperDiv.classList.add("message-wrapper");
    messageWrapperDiv.id = 'thinking'

    const thinkingDiv = document.createElement('div')
    thinkingDiv.classList.add('message')
    thinkingDiv.innerText = 'Copilot is thinking...'
    messageWrapperDiv.appendChild(thinkingDiv)

    messagesContainer.appendChild(messageWrapperDiv)
}

function stopThinking() {
    const thinkingDiv = document.getElementById('thinking')
    if (thinkingDiv && thinkingDiv.parentNode) {
        thinkingDiv.parentNode.removeChild(thinkingDiv)
    }
}


/**
 * Handling the minimize screen
 */
document.getElementById("minimize").addEventListener("click", () => {
    window.electron.minimize();
});

/**
 * Handling the screenshot button
 */
document.getElementById("screenshot").addEventListener("click", (event) => {
    window.electron.screenshot();
});
