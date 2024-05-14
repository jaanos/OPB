'use strict'

let filtriraj = function(niz, stolpci=[1]) {
    let podatki = document.getElementById("podatki");
    [...podatki.rows].forEach(vrstica => {
        if (vrstica.cells[0].tagName.toLocaleLowerCase() == "th") {
            return;
        }
        if (stolpci.some(stolpec =>
                vrstica.cells[stolpec].innerText.toLocaleLowerCase().indexOf(niz) >= 0)) {
            vrstica.style.display = '';
        } else {
            vrstica.style.display = 'none';
        }
    })
}

let preveri_geslo = function() {
    let ok = document.getElementById("geslo").value == document.getElementById("geslo2").value;
    if (!ok) {
        alert("Gesli se ne ujemata!")
    }
    return ok;
}
