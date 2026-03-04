// Dean Attali / Beautiful Jekyll 2023

let BeautifulJekyllJS = {

  bigImgEl : null,
  numImgs : null,
  searchData : null,
  searchPromise : null,
  searchSuggestions : [],

  init : function() {
    setTimeout(BeautifulJekyllJS.initNavbar, 10);

    // Shorten the navbar after scrolling a little bit down
    $(window).scroll(function() {
        if ($(".navbar").offset().top > 50) {
            $(".navbar").addClass("top-nav-short");
        } else {
            $(".navbar").removeClass("top-nav-short");
        }
    });

    // On mobile, hide the avatar when expanding the navbar menu
    $('#main-navbar').on('show.bs.collapse', function () {
      $(".navbar").addClass("top-nav-expanded");
    });
    $('#main-navbar').on('hidden.bs.collapse', function () {
      $(".navbar").removeClass("top-nav-expanded");
    });

    // show the big header image
    BeautifulJekyllJS.initImgs();

    BeautifulJekyllJS.initSearch();
  },

  initNavbar : function() {
    // Set the navbar-dark/light class based on its background color
    const rgb = $('.navbar').css("background-color").replace(/[^\d,]/g,'').split(",");
    const brightness = Math.round(( // http://www.w3.org/TR/AERT#color-contrast
      parseInt(rgb[0]) * 299 +
      parseInt(rgb[1]) * 587 +
      parseInt(rgb[2]) * 114
    ) / 1000);
    if (brightness <= 125) {
      $(".navbar").removeClass("navbar-light").addClass("navbar-dark");
    } else {
      $(".navbar").removeClass("navbar-dark").addClass("navbar-light");
    }
  },

  initImgs : function() {
    // If the page was large images to randomly select from, choose an image
    if ($("#header-big-imgs").length > 0) {
      BeautifulJekyllJS.bigImgEl = $("#header-big-imgs");
      BeautifulJekyllJS.numImgs = BeautifulJekyllJS.bigImgEl.attr("data-num-img");

      // 2fc73a3a967e97599c9763d05e564189
      // set an initial image
      const imgInfo = BeautifulJekyllJS.getImgInfo();
      const src = imgInfo.src;
      const desc = imgInfo.desc;
      BeautifulJekyllJS.setImg(src, desc);

      // For better UX, prefetch the next image so that it will already be loaded when we want to show it
      const getNextImg = function() {
        const imgInfo = BeautifulJekyllJS.getImgInfo();
        const src = imgInfo.src;
        const desc = imgInfo.desc;

        const prefetchImg = new Image();
        prefetchImg.src = src;
        // if I want to do something once the image is ready: `prefetchImg.onload = function(){}`

        setTimeout(function(){
          const img = $("<div></div>").addClass("big-img-transition").css("background-image", 'url(' + src + ')');
          $(".intro-header.big-img").prepend(img);
          setTimeout(function(){ img.css("opacity", "1"); }, 50);

          // after the animation of fading in the new image is done, prefetch the next one
          //img.one("transitioned webkitTransitionEnd oTransitionEnd MSTransitionEnd", function(){
          setTimeout(function() {
            BeautifulJekyllJS.setImg(src, desc);
            img.remove();
            getNextImg();
          }, 1000);
          //});
        }, 6000);
      };

      // If there are multiple images, cycle through them
      if (BeautifulJekyllJS.numImgs > 1) {
        getNextImg();
      }
    }
  },

  getImgInfo : function() {
    const randNum = Math.floor((Math.random() * BeautifulJekyllJS.numImgs) + 1);
    const src = BeautifulJekyllJS.bigImgEl.attr("data-img-src-" + randNum);
    const desc = BeautifulJekyllJS.bigImgEl.attr("data-img-desc-" + randNum);

    return {
      src : src,
      desc : desc
    }
  },

  setImg : function(src, desc) {
    $(".intro-header.big-img").css("background-image", 'url(' + src + ')');
    if (typeof desc !== typeof undefined && desc !== false) {
      $(".img-desc").text(desc).show();
    } else {
      $(".img-desc").hide();
    }
  },

  loadSearchIndex : function() {
    if (BeautifulJekyllJS.searchData) {
      return Promise.resolve(BeautifulJekyllJS.searchData);
    }
    if (BeautifulJekyllJS.searchPromise) {
      return BeautifulJekyllJS.searchPromise;
    }

    const overlay = document.getElementById("beautifuljekyll-search-overlay");
    if (!overlay) {
      return Promise.resolve([]);
    }

    const jsonUrl = overlay.dataset.searchJson;
    BeautifulJekyllJS.searchPromise = fetch(jsonUrl)
      .then(function(response) {
        if (!response.ok) {
          throw new Error("Unable to load search index");
        }
        return response.json();
      })
      .then(function(entries) {
        BeautifulJekyllJS.searchData = entries.map(function(entry) {
          const normalized = {
            title: entry.title || "",
            desc: entry.desc || "",
            author: entry.author || "",
            category: entry.category || "",
            url: entry.url || "",
            date: entry.date || ""
          };
          normalized.searchText = [
            normalized.title,
            normalized.desc,
            normalized.author,
            normalized.category,
            normalized.date
          ].join(" ").toLowerCase();
          return normalized;
        });
        BeautifulJekyllJS.searchSuggestions = BeautifulJekyllJS.buildSearchSuggestions(BeautifulJekyllJS.searchData);
        return BeautifulJekyllJS.searchData;
      })
      .catch(function(error) {
        BeautifulJekyllJS.searchPromise = null;
        throw error;
      });

    return BeautifulJekyllJS.searchPromise;
  },

  setSearchStatus : function(message) {
    const statusEl = document.getElementById("nav-search-status");
    if (!statusEl) {
      return;
    }
    statusEl.textContent = message;
  },

  buildSearchSuggestions : function(entries) {
    const fallback = ["Simplex", "HotStuff", "Partial synchrony", "Asynchrony", "Consensus"];
    const counts = new Map();

    entries.forEach(function(entry) {
      (entry.category || "")
        .split(",")
        .map(function(token) { return token.trim(); })
        .filter(function(token) { return token && token !== "post" && token !== "page"; })
        .forEach(function(token) {
          const key = token.toLowerCase();
          const current = counts.get(key) || { label: token, count: 0 };
          current.count += 1;
          counts.set(key, current);
        });
    });

    const dynamic = Array.from(counts.values())
      .sort(function(a, b) { return b.count - a.count; })
      .slice(0, 7)
      .map(function(item) { return item.label; });

    return Array.from(new Set(dynamic.concat(fallback))).slice(0, 8);
  },

  renderSearchSuggestions : function() {
    const suggestionsEl = document.getElementById("search-suggestions");
    if (!suggestionsEl) {
      return;
    }
    suggestionsEl.innerHTML = "";
    BeautifulJekyllJS.searchSuggestions.forEach(function(label) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "search-suggestion";
      button.textContent = label;
      button.addEventListener("click", function() {
        const input = document.getElementById("nav-search-input");
        if (!input) {
          return;
        }
        input.value = label;
        BeautifulJekyllJS.renderSearchResults(label);
        input.focus();
      });
      suggestionsEl.appendChild(button);
    });
  },

  highlightFirstSearchResult : function() {
    document.querySelectorAll(".search-result-link.active").forEach(function(el) {
      el.classList.remove("active");
    });
    const firstResult = document.querySelector(".search-result-link");
    if (firstResult) {
      firstResult.classList.add("active");
    }
    return firstResult;
  },

  renderSearchResults : function(query) {
    const resultsEl = document.getElementById("search-results-container");
    if (!resultsEl) {
      return;
    }

    const normalizedQuery = query.trim().toLowerCase();
    resultsEl.innerHTML = "";

    if (normalizedQuery.length < 2) {
      BeautifulJekyllJS.setSearchStatus("Start typing or pick a topic below.");
      BeautifulJekyllJS.renderSearchSuggestions();
      return;
    }

    if (!BeautifulJekyllJS.searchData) {
      BeautifulJekyllJS.setSearchStatus("Loading search index...");
      return;
    }

    const suggestionsEl = document.getElementById("search-suggestions");
    if (suggestionsEl) {
      suggestionsEl.innerHTML = "";
    }

    const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
    const scored = BeautifulJekyllJS.searchData
      .map(function(entry) {
        if (!tokens.every(function(token) { return entry.searchText.includes(token); })) {
          return null;
        }

        let score = 0;
        const title = entry.title.toLowerCase();
        const desc = entry.desc.toLowerCase();
        if (title === normalizedQuery) {
          score += 100;
        }
        if (title.startsWith(normalizedQuery)) {
          score += 40;
        }
        if (title.includes(normalizedQuery)) {
          score += 20;
        }
        score += tokens.filter(function(token) { return title.includes(token); }).length * 5;
        score += tokens.filter(function(token) { return desc.includes(token); }).length * 2;

        return { entry: entry, score: score };
      })
      .filter(Boolean)
      .sort(function(a, b) { return b.score - a.score; })
      .slice(0, 12);

    if (scored.length === 0) {
      BeautifulJekyllJS.setSearchStatus('No results for "' + query.trim() + '".');
      return;
    }

    BeautifulJekyllJS.setSearchStatus("Showing " + scored.length + " result" + (scored.length === 1 ? "" : "s") + ".");

    scored.forEach(function(result) {
      const item = document.createElement("li");
      item.className = "search-result";

      const link = document.createElement("a");
      link.href = result.entry.url;
      link.className = "search-result-link";

      const title = document.createElement("span");
      title.className = "search-result-title";
      title.textContent = result.entry.title || result.entry.url;
      link.appendChild(title);

      if (result.entry.desc) {
        const desc = document.createElement("span");
        desc.className = "search-result-desc";
        desc.textContent = result.entry.desc;
        link.appendChild(desc);
      }

      const metaParts = [result.entry.author, result.entry.date, result.entry.category].filter(Boolean);
      if (metaParts.length > 0) {
        const meta = document.createElement("span");
        meta.className = "search-result-meta";
        meta.textContent = metaParts.join(" · ");
        link.appendChild(meta);
      }

      item.appendChild(link);
      resultsEl.appendChild(item);
    });

    BeautifulJekyllJS.highlightFirstSearchResult();
  },

  initSearch : function() {
    const overlay = document.getElementById("beautifuljekyll-search-overlay");
    const searchLink = document.getElementById("nav-search-link");
    const searchInput = document.getElementById("nav-search-input");
    const searchExit = document.getElementById("nav-search-exit");
    const homeSearchTrigger = document.getElementById("home-search-trigger");

    if (!overlay || !searchLink || !searchInput || !searchExit) {
      return;
    }

    const openSearch = function(initialQuery) {
      overlay.style.display = "block";
      if (typeof initialQuery === "string") {
        searchInput.value = initialQuery;
      }
      searchInput.focus();
      if (!searchInput.value) {
        searchInput.select();
      }
      $("body").addClass("overflow-hidden");
      BeautifulJekyllJS.setSearchStatus("Loading search index...");
      BeautifulJekyllJS.loadSearchIndex()
        .then(function() {
          BeautifulJekyllJS.renderSearchResults(searchInput.value);
        })
        .catch(function() {
          BeautifulJekyllJS.setSearchStatus("Search is temporarily unavailable.");
        });
    };

    const closeSearch = function() {
      overlay.style.display = "none";
      $("body").removeClass("overflow-hidden");
    };

    $("#nav-search-link").click(function(e) {
      e.preventDefault();
      openSearch();
    });
    $("#nav-search-exit").click(function(e) {
      e.preventDefault();
      closeSearch();
    });
    searchInput.addEventListener("input", function() {
      BeautifulJekyllJS.renderSearchResults(searchInput.value);
    });
    searchInput.addEventListener("keydown", function(e) {
      if (e.key === "Enter") {
        const firstResult = BeautifulJekyllJS.highlightFirstSearchResult();
        if (firstResult) {
          window.location.href = firstResult.href;
        }
      }
    });
    if (homeSearchTrigger) {
      homeSearchTrigger.addEventListener("click", function() {
        openSearch();
      });
    }
    BeautifulJekyllJS.loadSearchIndex().catch(function() {});
    document.addEventListener("keydown", function(e) {
      if (e.key === "/" && !overlay.contains(document.activeElement)) {
        const tag = document.activeElement && document.activeElement.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA") {
          return;
        }
        e.preventDefault();
        openSearch();
      }
    });
    $(document).on('keyup', function(e) {
      if (e.key == "Escape") {
        closeSearch();
      }
    });
  }
};

// 2fc73a3a967e97599c9763d05e564189

document.addEventListener('DOMContentLoaded', BeautifulJekyllJS.init);
