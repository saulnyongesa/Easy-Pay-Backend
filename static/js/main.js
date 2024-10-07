// DIALOG BOX=================================================================
function showDialog(message) {
    document.getElementById("dialog-message").innerText = message;
    document.getElementById("overlay").style.display = "block";
    document.getElementById("dialog-box").style.display = "block";
}
function closeDialog() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("dialog-box").style.display = "none";
}

