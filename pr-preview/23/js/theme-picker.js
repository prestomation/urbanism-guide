// Transit Theme Picker
(function () {
  var STORAGE_KEY = "transit-theme";

  var themes = [
    { id: "", name: "Default", color: "#0055bb" },
    { id: "link", name: "Link Light Rail", color: "#008751" },
    { id: "metro", name: "King County Metro", color: "#003DA5" },
    { id: "sounder", name: "Sounder", color: "#6D2077" },
    { id: "ferries", name: "WA State Ferries", color: "#006747" },
    { id: "streetcar", name: "Seattle Streetcar", color: "#C8102E" },
  ];

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY) || "";
    } catch (e) {
      return "";
    }
  }

  function setTheme(themeId) {
    if (themeId) {
      document.documentElement.setAttribute("data-transit-theme", themeId);
    } else {
      document.documentElement.removeAttribute("data-transit-theme");
    }
    try {
      localStorage.setItem(STORAGE_KEY, themeId);
    } catch (e) {
      // localStorage unavailable
    }
  }

  function initPicker() {
    var picker = document.getElementById("theme-picker");
    if (!picker) return;

    var swatchContainer = picker.querySelector(".theme-picker-swatches");
    var nameDisplay = picker.querySelector(".theme-picker-name");
    var currentTheme = getStoredTheme();

    // Build swatch buttons
    themes.forEach(function (theme) {
      var btn = document.createElement("button");
      btn.className = "theme-swatch" + (theme.id === currentTheme ? " active" : "");
      btn.setAttribute("data-theme", theme.id);
      btn.setAttribute("title", theme.name);
      btn.setAttribute("aria-label", theme.name + " theme");
      btn.style.setProperty("--swatch-color", theme.color);

      btn.addEventListener("click", function () {
        setTheme(theme.id);

        // Update active state
        var allSwatches = swatchContainer.querySelectorAll(".theme-swatch");
        for (var i = 0; i < allSwatches.length; i++) {
          allSwatches[i].classList.remove("active");
        }
        btn.classList.add("active");

        // Update name display
        if (nameDisplay) {
          nameDisplay.textContent = theme.name;
        }
      });

      swatchContainer.appendChild(btn);
    });

    // Set initial name display
    var activeTheme = themes.filter(function (t) {
      return t.id === currentTheme;
    })[0];
    if (nameDisplay && activeTheme) {
      nameDisplay.textContent = activeTheme.name;
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPicker);
  } else {
    initPicker();
  }
})();
