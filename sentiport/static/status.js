function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(';').shift()
    return null
}

function initRenderTaskAlert(
    threadID,
    playstoreID,
    countryCode,
    userEmail 
) {
    // define html
    alertHTML = `
    <div id="${threadID}" class="alert alert-info alert-dismissible fade show" role="alert">
        <h4 id="${threadID}-heading" class="alert-heading">Working on it..</h4>
        <hr>
        <div class="mb-0">
            <span id="${threadID}-desc">Sending</span> <strong>${playstoreID}</strong> <strong>(${countryCode})</strong> report to <strong>${userEmail}</strong>
        </div>
    </div>
    `
    $("#status").append(alertHTML) // appendChild
    $("#submit-button").prop("disabled", true) // disable button 
}

function modifyTaskAlert(threadID, isRunning, isError, runtimeMessage) {
    try {
        if (!isRunning) {
            //add close button
            closeButton = `
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span> 
            </button>
            `
            $(`#${threadID}`).append(closeButton)
            $("#submit-button").prop("disabled", false) // re-enable button
            
            //if task finished successfully
            if (!isError) {
                $(`#${threadID}`).removeClass("alert-info").addClass("alert-success")
                $(`#${threadID}-heading`).html("Email sent")
                $(`#${threadID}-desc`).html("Successfully sent")
            }
            //if task finished with an error
            else {
                $(`#${threadID}`).removeClass("alert-info").addClass("alert-danger")
                $(`#${threadID}-heading`).html("Sorry, something went wrong")
                $(`#${threadID}-desc`).html("Failed to send")
            }            
        }
        else {
            $(`#${threadID}-heading`).html(runtimeMessage)
        }
    }
    catch (err) {
        console.log(err)
    }
}

async function periodicStatusCheck(statusURL, threadID) {
    let isActive = false
    await fetch(statusURL)
            .then(res => res.json())
            .then(res => {
                let isRunning = res["task_status"]["isRunning"]
                let isError = res["task_status"]["isError"]
                let runtimeMessage = res["task_status"]["runtimeMessage"]

                modifyTaskAlert(threadID, isRunning, isError, runtimeMessage)

                if (isRunning && !isError) {
                    isActive = true
                }
            }) 
            .catch(err => console.log(err))

    if (isActive) {
        setTimeout(() => periodicStatusCheck(statusURL, threadID), 10000)
    }
    else {
        await fetch("status/delete", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "thread_id": threadID
            })
        })
        .catch(err => console.log(err))
    }
}

