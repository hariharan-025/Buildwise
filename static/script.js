document.querySelectorAll(".build-progress-fill").forEach(function (bar) {
    var percent = bar.dataset.progress || 0;
    bar.style.width = percent + "%";
});

document.querySelectorAll(".specs-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
        var card = btn.closest(".flip-card");
        if (card) {
            card.classList.toggle("is-flipped");
        }
    });
});

// Ask for confirmation before wiping the current PC build,
// since Reset Build removes every selected component at once.
var resetForm = document.querySelector('form[action*="builder/reset"]');
if (resetForm) {
    resetForm.addEventListener("submit", function (e) {
        var confirmed = window.confirm("Reset your build? This will remove every selected component.");
        if (!confirmed) {
            e.preventDefault();
        }
    });
}
// Pre-Built PC hero carousel (structure only for now — slides are static
// placeholder content until a real Pre-Built PC model/view exists).
var prebuildCarousel = document.getElementById("prebuildCarousel");
if (prebuildCarousel) {
    var track = prebuildCarousel.querySelector(".prebuild-track");
    var slides = prebuildCarousel.querySelectorAll(".prebuild-slide");
    var dots = prebuildCarousel.querySelectorAll(".prebuild-dot");
    var currentSlide = 0;


    function goToSlide(index) {
        currentSlide = (index + slides.length) % slides.length;
        track.style.transform = "translateX(-" + (currentSlide * 100) + "%)";
        dots.forEach(function (dot, i) {
            dot.classList.toggle("active", i === currentSlide);
        });
    }

    var prevBtn = prebuildCarousel.querySelector(".prebuild-prev");
    var nextBtn = prebuildCarousel.querySelector(".prebuild-next");
    if (prevBtn) prevBtn.addEventListener("click", function () { goToSlide(currentSlide - 1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { goToSlide(currentSlide + 1); });

    dots.forEach(function (dot, i) {
        dot.addEventListener("click", function () { goToSlide(i); });
    });

    // Gentle autoplay, paused while the user is hovering the carousel.
    var prebuildAutoplay = setInterval(function () { goToSlide(currentSlide + 1); }, 6000);
    prebuildCarousel.addEventListener("mouseenter", function () { clearInterval(prebuildAutoplay); });
    prebuildCarousel.addEventListener("mouseleave", function () {
        prebuildAutoplay = setInterval(function () { goToSlide(currentSlide + 1); }, 6000);
    });
}

// Pre-Built PC filter pills — visual toggle only for now. There's no
// filtering logic yet because there's no Pre-Built PC data in the
// database; this just previews the interaction for later.
document.querySelectorAll(".prebuild-filter-pill").forEach(function (pill) {
    pill.addEventListener("click", function () {
        document.querySelectorAll(".prebuild-filter-pill").forEach(function (p) {
            p.classList.remove("active");
        });
        pill.classList.add("active");
    });
});
// Accessories category filter. Pills reuse the existing
// ".prebuild-filter-pill" active-state toggle (see above), so this only
// handles showing/hiding the matching product cards, plus keeping the
// selected category in the URL (?category=...) the same way the
// Pre-Build page's filter does, so links from the hero carousel land
// on the right filter already applied.
var accessoryPills = document.querySelectorAll("#accessoryFilters .prebuild-filter-pill");
var accessoryCards = document.querySelectorAll(".accessory-card");
var accessoryNoMatch = document.getElementById("accessoryNoMatch");

function applyAccessoryFilter(filter) {
    var visibleCount = 0;
    accessoryCards.forEach(function (card) {
        var matches = filter === "all" || card.dataset.category === filter;

        if (matches) {
            visibleCount += 1;
            card.classList.remove("accessory-card-hidden");
            // Fade the card in on the next frame so newly-shown cards
            // transition smoothly instead of just popping into view.
            requestAnimationFrame(function () {
                card.classList.add("accessory-card-visible");
            });
        } else {
            card.classList.remove("accessory-card-visible");
            card.classList.add("accessory-card-hidden");
        }
    });

    if (accessoryNoMatch) {
        accessoryNoMatch.hidden = visibleCount !== 0 || accessoryCards.length === 0;
    }

    accessoryPills.forEach(function (pill) {
        pill.classList.toggle("active", pill.dataset.filter === filter);
    });
}

if (accessoryPills.length && accessoryCards.length) {
    var initialAccessoryFilter = new URL(window.location.href).searchParams.get("category") || "all";
    applyAccessoryFilter(initialAccessoryFilter);

    accessoryPills.forEach(function (pill) {
        pill.addEventListener("click", function () {
            applyAccessoryFilter(pill.dataset.filter);
            var url = new URL(window.location.href);
            if (pill.dataset.filter === "all") {
                url.searchParams.delete("category");
            } else {
                url.searchParams.set("category", pill.dataset.filter);
            }
            window.history.replaceState({}, "", url);
        });
    });
}