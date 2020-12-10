function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(';').shift()
    return null
}

async function periodicStatusCheck(statusURL="") {
    let statusDiv = document.getElementById("status")
    let isActive = false
    await fetch(statusURL)
            .then(res => res.json())
            .then(res => {
                let isRunning = res["task_status"]["isRunning"]
                let isError = res["task_status"]["isError"]
                statusDiv.innerHTML = `isRunning: ${isRunning}, isError: ${isError}`
                
                if (isRunning && !isError) {
                    isActive = true
                }
            }) 
            .catch(err => console.log(err))

    if (isActive){
        setTimeout(() => periodicStatusCheck(statusURL), 2000)
    }
}

function TO_BE_DELETED_getStatus(statusURL) {
    fetch(statusURL)
    .then(res => res.json())
    .then(res => {
        document.getElementById("status").innerHTML = "ardy"//JSON.stringify(res)
    })
    .then(() => {
        setTimeout(() => getStatus(statusURL), 1000)
        console.log("hellow?")
    })
    .catch(err => console.log(err))
}

function TO_BE_DELETED_onFormSubmit() {
    let playstoreID = document.getElementById("playstore_id")
    let countryID = document.getElementById("country_code")
    let email = document.getElementById("user_email")

    fetch("/scrape", {
        method: "POST",
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify({
            "playstore_id": playstoreID.value,
            "country_code": countryID.value,
            "user_email": email.value
        })
    })
    .then(res => res.json())
    .then(res => {
        if (res["status"] == 202) {
            playstoreID.value = ""
            countryID.value = ""
            email.value = ""
            return res
        }
        throw Error
    })
    .then(res => getStatus(res["url"]))
    .catch(err => console.log(err))
}

// DEBUG
document.getElementById("playstore_id").value = "in.goodapps.besuccessful"
document.getElementById("country_code").value = "US"
document.getElementById("user_email").value = "afharoen@gmail.com"

periodicStatusCheck()