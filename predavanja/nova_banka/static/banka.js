'use strict'

function isci(stolpci = [1]) {
    let vrednost = document.getElementById('isci').value;
    let tabela = document.getElementById('izpis');
    [...tabela.rows].forEach(vrstica => {       
       if(stolpci.some(stolpec => seUjema(vrstica, stolpec, vrednost))) {
          vrstica.style.display = ''
       } else {
         vrstica.style.display = 'none'
       }
    })
}  

function seUjema(vrstica, stolpec, vrednost) {
    let vsebina = vrstica.cells[stolpec].innerText
    return vsebina.toLocaleLowerCase().indexOf(vrednost.toLocaleLowerCase()) >= 0
}


