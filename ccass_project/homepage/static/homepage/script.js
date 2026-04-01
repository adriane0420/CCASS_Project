window.addEventListener("scroll", function () {
    let navbar = document.querySelector(".navbar");
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
});


/*scroll*/
const sections = document.querySelectorAll(".section");
let currentIndex = 0;
let isScrolling = false;

function goToSection(index) {
  if (index < 0 || index >= sections.length) return;

  isScrolling = true;
  currentIndex = index;

  sections[index].scrollIntoView({
    behavior: "smooth"
  });

  setTimeout(() => {
    isScrolling = false;
  }, 700); // adjust speed
}

window.addEventListener("wheel", (e) => {
  if (isScrolling) return;

  if (e.deltaY > 0) {
    goToSection(currentIndex + 1);
  } else {
    goToSection(currentIndex - 1);
  }
});