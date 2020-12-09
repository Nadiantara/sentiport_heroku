function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null
}

async function periodicStatusCheck() {
    statusURL = getCookie("status_url")
    statusDiv = document.getElementById("status")
    if(statusURL) {
        status = await fetch(statusURL)
                        .then(res => res.json())
                        .then(res => {
                            statusDiv.innerHTML = `isRunning: ${res["task_status"]["isRunning"]}, isError: ${res["task_status"]["isError"]}`
                        }) 
                        .catch(err => console.log(err))
    }
    else {
        statusDiv.innerHTML = "nothing here"
    }
        
    setTimeout(() => periodicStatusCheck(), 2000)
}

function getStatus(statusURL) {
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

function onFormSubmit() {
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