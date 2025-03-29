
document.addEventListener("DOMContentLoaded", function() {
// Fade in on page load (as above)
document.body.classList.add("fade-in");

// Attach click events to all internal links
document.querySelectorAll("a").forEach(function(link) {
  // Check if the link is internal by comparing hostnames
  if (link.hostname === window.location.hostname) {
    link.addEventListener("click", function(event) {
      // Prevent immediate navigation
      event.preventDefault();
      // Remove the 'fade-in' class to trigger fade out
      document.body.classList.remove("fade-in");
      // Wait for the transition to finish (300ms here) then navigate
      setTimeout(function() {
        window.location = link.href;
      }, 300); // Adjust this delay to match your CSS transition duration
    });
  }
});
});
