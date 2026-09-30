const catalogEl = document.querySelector("#catalog");
const filtersEl = document.querySelector("#filters");
const summaryEl = document.querySelector("#summary");
const generatedEl = document.querySelector("#generated");
const queryEl = document.querySelector("#query");

const state = {
  category: "All",
  query: "",
  projects: [],
  categories: [],
};

function matches(project) {
  if (state.category !== "All" && project.category !== state.category) return false;
  const needle = state.query.trim().toLowerCase();
  if (!needle) return true;
  return [project.name, project.description, project.language, project.category, ...(project.topics || [])]
    .join(" ")
    .toLowerCase()
    .includes(needle);
}

function render() {
  const visible = state.projects.filter(matches);
  if (!visible.length) {
    catalogEl.replaceChildren(el("li", { class: "repo-empty", text: "No repositories match." }));
    return;
  }
  catalogEl.replaceChildren(...visible.map((project) => repoCard(project)));
}

function renderFilters() {
  const counts = { All: state.projects.length };
  for (const project of state.projects) counts[project.category] = (counts[project.category] || 0) + 1;

  filtersEl.replaceChildren(
    ...["All", ...state.categories].map((name) => {
      const button = el(
        "button",
        { type: "button", role: "tab", "aria-selected": name === state.category ? "true" : "false" },
        name,
        el("span", { class: "count", text: String(counts[name] || 0) }),
      );
      button.addEventListener("click", () => {
        state.category = name;
        for (const other of filtersEl.querySelectorAll("button")) {
          other.setAttribute("aria-selected", other === button ? "true" : "false");
        }
        render();
      });
      return button;
    }),
  );
}

queryEl.addEventListener("input", () => {
  state.query = queryEl.value;
  render();
});

loadCatalog()
  .then((data) => {
    state.projects = data.projects;
    state.categories = data.categories;
    const mirrors = data.projects.filter((project) => project.gitlab).length;
    summaryEl.textContent = `${data.projects.length} public original repositories, ${mirrors} mirrored to GitLab. Sorted by most recent push.`;
    generatedEl.textContent = data.generated ? `Index generated ${data.generated}.` : "";
    renderFilters();
    render();
  })
  .catch(() => {
    summaryEl.textContent = "The project index could not be loaded.";
  });
