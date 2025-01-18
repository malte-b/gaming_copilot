const messagesContainer = document.querySelector('.messages-container')

document.getElementById('minimize').addEventListener("click", () => {
    window.electron.minimize()
})

/** 
 * Handling the case when user submits the form either by clicking on search button
 * or pressing enter key
 */
document.getElementById('input-form').addEventListener('submit', event => {
    event.preventDefault()

    const formData = new FormData(event.target)
    appendMessage(formData.get('query'), 'user')

    event.target.reset()
})

function appendMessage(message, by) {
    // Creating outer div of message
    const messageWrapperDiv = document.createElement('div')
    messageWrapperDiv.classList.add('message-wrapper')

    // Flex reverse if message is by user
    if (by === 'user') {
        messageWrapperDiv.classList.add('reverse')
    }

    // Creating actual message `p`
    const messageP = document.createElement('p')
    messageP.classList.add('message')
    messageP.innerText = message

    // Appending message `p` to div
    messageWrapperDiv.appendChild(messageP)

    // Apending div to our messages container
    messagesContainer.appendChild(messageWrapperDiv)
}