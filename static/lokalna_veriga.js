'use strict'

function isci() {
    let vrednost = document.getElementById('isci').value;
    let tabela = document.getElementById('izpis');
    [...tabela.rows].forEach(vrstica => {
        let vsebina = vrstica.cells[1].innerText
        if(vsebina.toLocaleLowerCase().indexOf(vrednost.toLocaleLowerCase()) >= 0) {
            vrstica.style.display = ''
        } else {
            vrstica.style.display = 'none'
        }
    })
}