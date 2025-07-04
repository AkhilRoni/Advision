let stars = document.getElementById('stars');
let moon = document.getElementById('moon');
let mountains_behind = document.getElementById('mountains_behind');
let mountains_front = document.getElementById('mountains_front');

window.addEventListener('scroll', function() {
  let value = this.window.scrollY;
  stars.style.left = value * 0.25 + 'px';
  moon.style.top = value * 1.05 + 'px';
  mountains_behind.style.top = value * 0.5 + 'px';
  mountains_front.style.top = value * 0 + 'px';
})

document.addEventListener('DOMContentLoaded', () => {
  const elements = document.querySelectorAll('.hidden, h2, h3, p, .text-box, .img-container img');

  const checkVisibility = () => {
    elements.forEach(element => {
      const elementTop = element.getBoundingClientRect().top;
      const elementBottom = element.getBoundingClientRect().bottom;
      const isVisible = (elementTop < window.innerHeight) && (elementBottom > 0);

      if (isVisible) {
        element.classList.add('visible');
      } else {
        element.classList.remove('visible'); // Remove the class when out of view
      }
    });
  };

  window.addEventListener('scroll', checkVisibility);
  checkVisibility(); // Check on initial load
});
