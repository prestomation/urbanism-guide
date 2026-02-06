// Transit Theme Picker
(function () {
  var STORAGE_KEY = "transit-theme";

  var themes = [
    { id: "", name: "Default", light: null, dark: null, swatch: "#0055bb" },
    {
      id: "link",
      name: "Link Light Rail",
      swatch: "#008751",
      light: { link: "#008751", visited: "#005c37" },
      dark: { link: "#5ce0a8", visited: "#3ec48e" },
    },
    {
      id: "metro",
      name: "King County Metro",
      swatch: "#003DA5",
      light: { link: "#003DA5", visited: "#1a2e6e" },
      dark: { link: "#7daaff", visited: "#a0b8ff" },
    },
    {
      id: "sounder",
      name: "Sounder",
      swatch: "#6D2077",
      light: { link: "#6D2077", visited: "#4c1654" },
      dark: { link: "#c88dd4", visited: "#d4a8dd" },
    },
    {
      id: "ferries",
      name: "WA State Ferries",
      swatch: "#006747",
      light: { link: "#006747", visited: "#004832" },
      dark: { link: "#5cc8a8", visited: "#42b094" },
    },
    {
      id: "streetcar",
      name: "Seattle Streetcar",
      swatch: "#C8102E",
      light: { link: "#C8102E", visited: "#9e0c24" },
      dark: { link: "#ff7a87", visited: "#ff9ca5" },
    },
  ];

  var currentThemeId = "";

  function isDark() {
    return (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  }

  function findTheme(id) {
    for (var i = 0; i < themes.length; i++) {
      if (themes[i].id === id) return themes[i];
    }
    return themes[0];
  }

  function applyColors(theme) {
    var el = document.documentElement;
    if (!theme || !theme.light) {
      // Default theme: remove inline overrides, let stylesheet handle it
      el.style.removeProperty("--color-link");
      el.style.removeProperty("--color-visited-link");
      return;
    }
    var colors = isDark() ? theme.dark : theme.light;
    el.style.setProperty("--color-link", colors.link);
    el.style.setProperty("--color-visited-link", colors.visited);
  }

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY) || "";
    } catch (e) {
      return "";
    }
  }

  function setTheme(themeId) {
    currentThemeId = themeId;
    var theme = findTheme(themeId);
    applyColors(theme);
    try {
      localStorage.setItem(STORAGE_KEY, themeId);
    } catch (e) {
      // localStorage unavailable
    }
  }

  // Re-apply colors when system dark/light mode changes
  if (window.matchMedia) {
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", function () {
        var theme = findTheme(currentThemeId);
        applyColors(theme);
      });
  }

  function initPicker() {
    var picker = document.getElementById("theme-picker");
    if (!picker) return;

    var swatchContainer = picker.querySelector(".theme-picker-swatches");
    var nameDisplay = picker.querySelector(".theme-picker-name");
    currentThemeId = getStoredTheme();

    // Apply saved theme
    setTheme(currentThemeId);

    // Build swatch buttons
    themes.forEach(function (theme) {
      var btn = document.createElement("button");
      btn.className =
        "theme-swatch" + (theme.id === currentThemeId ? " active" : "");
      btn.setAttribute("data-theme", theme.id);
      btn.setAttribute("title", theme.name);
      btn.setAttribute("aria-label", theme.name + " theme");
      btn.style.setProperty("--swatch-color", theme.swatch);

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
    var activeTheme = findTheme(currentThemeId);
    if (nameDisplay) {
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
