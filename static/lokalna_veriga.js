'use strict'

function isci(stolpci = [1]) {
    let vrednost = document.getElementById('isci').value;
    let tabela = document.getElementById('izpis');
    [...tabela.rows].forEach(vrstica => {
        if(stolpci.some(stolpec => seUjema(vrstica, stolpec, vrednost))) { // some = vsaj eden mora biti true
            vrstica.style.display = ''
        } else {
            vrstica.style.display = 'none'
        }
    })
}

function seUjema(vrstica, stolpec, vrednost) { // ali se vrstica v stulpcu 'stolpec' ujema z vrednostjo
    let vsebina = vrstica.cells[stolpec].innerText
    return vsebina.toLocaleLowerCase().indexOf(vrednost.toLocaleLowerCase()) >= 0
}
