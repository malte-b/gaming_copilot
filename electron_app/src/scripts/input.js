const messagesContainer = document.querySelector(".messages-container");
const screenshotContainer = document.getElementById('screenshot-container')

const SCREENSHOT_ENDPOINT = 'http://localhost:5000/vision-screenshot-endpoint/'
const GENERAL_MESSAGE_ENDPOINT = 'http://localhost:5000/generate-langchain-response-endpoint/'

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

        const screenshot = formData.get('screenshot')
        const payload = { user_message }
        if (screenshot) {
            payload.image = screenshot
            appendMessage(screenshot, "image-url", true)
        }

        // Cleanup when user submits the form
        appendMessage(user_message, "user-message")
        event.target.reset()
        screenshotContainer.classList.remove('visible')

        startThinking()


        const source = new SSE(
            screenshot ? SCREENSHOT_ENDPOINT : GENERAL_MESSAGE_ENDPOINT,
            {
                payload: JSON.stringify(payload),
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


function appendMessage(message, type, isScreenshot = false) {
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
        messageImg.src = isScreenshot ? `data:image/png;base64,${message}` : message
        messageImg.classList.add(isScreenshot ? 'screenshot-img' : 'message-img')

        if (isScreenshot) {
            messageWrapperDiv.classList.add('reverse')
        }


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

/**
 * Handling the case when main process has taken a screenshot and sends us an event
 */
document.addEventListener("DOMContentLoaded", () => {
    window.electron.screenshotTaken(data => {
        const img = document.createElement('img')
        img.src = data

        const screenshotInput = document.createElement('input')
        screenshotInput.value = data.replace("data:image/png;base64,", "")
        screenshotInput.name = 'screenshot'
        screenshotInput.setAttribute('type', 'hidden')
        screenshotContainer.appendChild(screenshotInput)

        screenshotContainer.appendChild(img)
        screenshotContainer.classList.add('visible')
    })
})