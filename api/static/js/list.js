/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function drop_pr() {
  console.log('working')
  document.getElementById("my-drop-pr").classList.toggle("show");
}

function drop_pa() {
  console.log('working')
  document.getElementById("my-drop-pa").classList.toggle("show");
}

function drop_cl() {
  console.log('working')
  document.getElementById("my-drop-cl").classList.toggle("show");
}

function drop_of() {
  console.log('working')
  document.getElementById("my-drop-of").classList.toggle("show");
}

function drop_ca() {
  console.log('working')
  document.getElementById("my-drop-ca").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = document.getElementsByClassName("drop-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
} 