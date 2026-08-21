const links = [...document.querySelectorAll('.nav-link')];
const sections = links.map(link => document.querySelector(link.getAttribute('href')));
const menuButton = document.getElementById('menuButton');
const sidebar = document.getElementById('sidebar');
const themeButton = document.getElementById('themeButton');

const storedTheme = localStorage.getItem('resume-agent-docs-theme');
if (storedTheme === 'dark') document.body.classList.add('dark');

themeButton.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('resume-agent-docs-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
});

menuButton.addEventListener('click', () => sidebar.classList.toggle('open'));
links.forEach(link => link.addEventListener('click', () => sidebar.classList.remove('open')));

const observer = new IntersectionObserver(entries => {
  const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${visible.target.id}`));
}, { rootMargin: '-18% 0px -68% 0px', threshold: [0, .1, .5] });
sections.forEach(section => observer.observe(section));
