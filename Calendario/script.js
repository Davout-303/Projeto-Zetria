const datas = document.querySelector('.datas');
const header = document.querySelector('.calendario h3');
const nav = document.querySelectorAll('#anterior, #proximo');
const meses = [
    "Janeiro","Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"

];

let date = new Date();
let month = date.getMonth();
let year = date.getFullYear();

function renderCalendar(){
    
    let datasHtml = '';

    const start = new Date(year, month, 1).getDay();
    const endDate = new Date(year, month + 1, 0).getDate();

    const end = new Date(year, month, endDate).getDay();
    const endDatePrev = new Date(year, month, 0).getDate();

    for(let i = start; i > 0; i--){
        datasHtml += `<li class="inactive">${endDatePrev - i + 1}</li>`;
    }

    for(let i = 1; i <= endDate; i++){
        let className = (
            i === date.getDate() &&
            month === new Date().getMonth() && 
            year === new Date().getFullYear()
            ? ' class="today"' 
            :""
        );
        datasHtml += `<li${className}>${i}</li>`;
    }
    

    for(let i = end; i < 6; i++){
        datasHtml += `<li class="inactive">${i - end + 1}</li>`;

    }


    datas.innerHTML = datasHtml;
    header.textContent = `${meses[month]} ${year}`;

}
nav.forEach(nav => {
    nav.addEventListener('click', e => {
        const btnId = e.target.id;
        if(btnId === 'anterior' && month === 0){
          year--;
          month = 11; // Correção aqui, voltar para dezembro (índice 11)
        }

        else if(btnId === 'proximo' && month === 11){
            year++;
            month = 0; // Correção aqui, avançar para janeiro (índice 0)
        }

        else{
          // Correção aqui, verificando se o ID é 'anterior' ou 'proximo'
          month = (btnId === 'proximo') ? month + 1 : month - 1;
        }

        date = new Date(year, month, new Date().getDate());
        year = date.getFullYear();
        month = date.getMonth();
        renderCalendar();
    })
})
    


renderCalendar();


