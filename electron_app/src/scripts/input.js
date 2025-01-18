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
            return;
        }

        appendMessage(user_message, "user-message")

        const source = new SSE(
            "http://localhost:5000/generate-langchain-response-endpoint/",
            {
                payload: JSON.stringify({ user_message }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: "POST",
            }
        );

        source.addEventListener("message", function (event) {
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
        const messageP = document.createElement("p");
        messageP.classList.add("message");
        messageP.innerText = message;

        // Appending message `p` to div
        messageWrapperDiv.appendChild(messageP);
    }

    // Apending div to our messages container
    messagesContainer.appendChild(messageWrapperDiv);
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
