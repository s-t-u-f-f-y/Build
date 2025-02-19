
const iconMenu = document.querySelector('.menu__icon');
if(iconMenu){
    const menuBody = document.querySelector('.menu__list')
    iconMenu.addEventListener("click", function(e){
        document.body.classList.toggle('_lock')
        iconMenu.classList.toggle('_active')
        menuBody.classList.toggle('_active')
    });
}


document.addEventListener('mousemove', parallax);

function parallax(e){
    document.querySelectorAll('.decor').forEach(function (move){

        const speedValue = move.getAttribute('data-value');

        let x = (e.clientX * speedValue / 100);
        let y = (e.clientY * speedValue / 75);

        move.style.transform = 'translateX(' + x + 'px) translateY(' + y + 'px)'

    });
}


const goTopBtn = document.querySelector(".go-top");

window.addEventListener("scroll", scrollEvent);
goTopBtn.addEventListener("click", goTop);

function scrollEvent(e){
    const scrolled = window.pageYOffset;

    const coords = document.documentElement.clientHeight;

    if (scrolled > coords) {
        // кнопка появляется
        goTopBtn.classList.add("_show");
      } else {
        // иначе исчезает
        goTopBtn.classList.remove("_show");
      }
}

function goTop() {
    if (window.pageYOffset > 0) {
      window.scrollBy(0, -25); 
      setTimeout(goTop, 0); 
    }
}

const popup = document.querySelector(".popup");
const popupBtn = document.getElementById("popupBtn");
const popupClose = document.querySelector(".close");
const popupBg = document.getElementById("popupBg");

popupBtn.addEventListener("click", clickBtn);
popupClose.addEventListener("click", closeBth);
window.addEventListener("click", closeWindow);

function clickBtn(){
    popup.classList.toggle("_active");
    popupBg.classList.toggle("_active");
}

function closeBth(){
    popup.classList.remove("_active")
    popupBg.classList.remove("_active");
}

function closeWindow(e){
    if(e.target == popup){
        popup.classList.remove("_active")
    }
}

const smoothLinks = document.querySelectorAll('a[href^="#"]');
for (let smoothLink of smoothLinks) {
    smoothLink.addEventListener('click', function (e) {
        e.preventDefault();
        const id = smoothLink.getAttribute('href');

        document.querySelector(id).scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
}