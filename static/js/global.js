document.addEventListener("DOMContentLoaded", function () {
  const menuToggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector("nav");

  menuToggle.addEventListener("click", function () {
    nav.classList.toggle("active");
  });

  document.addEventListener("click", function (event) {
    const isClickInsideNav = nav.contains(event.target);
    const isClickOnToggle = menuToggle.contains(event.target);

    if (
      !isClickInsideNav &&
      !isClickOnToggle &&
      nav.classList.contains("active")
    ) {
      nav.classList.remove("active");
    }
  });

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();

      const targetId = this.getAttribute("href");
      if (targetId === "#") return;

      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80,
          behavior: "smooth",
        });
      }
    });
  });

  const animateOnScroll = function () {
    const elements = document.querySelectorAll(
      ".feature-card, .about-content, .section-header"
    );

    elements.forEach((element) => {
      const elementPosition = element.getBoundingClientRect().top;
      const windowHeight = window.innerHeight;

      if (elementPosition < windowHeight - 50) {
        element.classList.add("fade-in");
      }
    });
  };

  const elementsToAnimate = document.querySelectorAll(
    ".feature-card, .about-content, .section-header"
  );
  elementsToAnimate.forEach((element) => {
    element.classList.add("to-animate");
  });

  const style = document.createElement("style");
  style.textContent = `
        .to-animate {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .fade-in {
            opacity: 1;
            transform: translateY(0);
        }
    `;
  document.head.appendChild(style);

  window.addEventListener("scroll", animateOnScroll);
  animateOnScroll();

  const header = document.querySelector("header");
  const makeHeaderSticky = function () {
    if (window.scrollY > 10) {
      header.classList.add("sticky");
      if (!document.querySelector(".sticky-style")) {
        const stickyStyle = document.createElement("style");
        stickyStyle.classList.add("sticky-style");
        stickyStyle.textContent = `
                    .sticky {
                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                        transition: all 0.3s ease;
                    }
                `;
        document.head.appendChild(stickyStyle);
      }
    } else {
      header.classList.remove("sticky");
    }
  };

  window.addEventListener("scroll", makeHeaderSticky);
  makeHeaderSticky();

  const featureCards = document.querySelectorAll(".feature-card");

  featureCards.forEach((card) => {
    card.addEventListener("mouseover", function () {
      this.style.boxShadow = "0 10px 25px rgba(78, 115, 223, 0.15)";
    });

    card.addEventListener("mouseout", function () {
      this.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.05)";
    });
  });

  const addCounterAnimation = function () {
    if (!document.querySelector(".counter-section")) {
      console.log("Counter section tidak ada di halaman ini.");
      return;
    }

    const counters = document.querySelectorAll(".counter");

    counters.forEach((counter) => {
      const target = parseInt(counter.getAttribute("data-target"));
      const duration = 2000;
      const steps = 50;
      const stepValue = target / steps;
      let current = 0;

      const updateCounter = setInterval(function () {
        current += stepValue;

        if (current >= target) {
          counter.textContent = target;
          clearInterval(updateCounter);
        } else {
          counter.textContent = Math.round(current);
        }
      }, duration / steps);
    });
  };

  if (document.querySelector(".counter-section")) {
    const counterObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            addCounterAnimation();
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );

    counterObserver.observe(document.querySelector(".counter-section"));
  }

  const preloader = document.querySelector(".preloader");
  if (preloader) {
    window.addEventListener("load", function () {
      preloader.style.opacity = "0";
      setTimeout(function () {
        preloader.style.display = "none";
      }, 500);
    });
  }

  const phoneInput = document.getElementById("phone");

  if (phoneInput) {
    phoneInput.addEventListener("input", function (e) {
      let value = e.target.value;

      let cleanedValue = value.replace(/[^0-9-+\s()]/g, "");

      if (value !== cleanedValue) {
        e.target.value = cleanedValue;
      }
    });
  }
});
