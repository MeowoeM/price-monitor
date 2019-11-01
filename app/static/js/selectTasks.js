function enterSelectingMode() {
    document.getElementById('select-button').classList.add("is-hidden")
    document.getElementById('display-button').classList.remove("is-hidden")
    document.getElementById('cancel-button').classList.remove("is-hidden")
}

function exitSelectingMode() {
    document.getElementById('select-button').classList.remove("is-hidden")
    document.getElementById('display-button').classList.add("is-hidden")
    document.getElementById('cancel-button').classList.add("is-hidden")

    var tasks = Array.prototype.slice.call(document.querySelectorAll('#task-list li'), 0);
    tasks.forEach(task => {
        if (task.classList.contains("active")) {
            task.classList.remove("active")
        }
    });
}

function displayMultipleTask() {
    var selectedTasksStr = ''
    var tasks = Array.prototype.slice.call(document.querySelectorAll('#task-list li'), 0);
    tasks.forEach(task => {
        if (task.classList.contains("active")) {
            selectedTasksStr = selectedTasksStr.concat('|', String(task.id))
        }
    });

    if (selectedTasksStr.length > 0) {
        selectedTasksStr = selectedTasksStr.substring(1)
        window.location.href = '../tasks/'.concat(selectedTasksStr)
    }
}

function selectTask(id) {
    isInSelectMode = !document.getElementById("select-button").classList.contains("is-hidden")
    if (isInSelectMode) {
        return true
    }
    else {
        task = document.getElementById(id)
        if (task.classList.contains("active")) {
            task.classList.remove("active")
        }
        else {
            task.classList.add("active")
        }
        return false
    }
}