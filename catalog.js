const catalogEl = document.querySelector("#catalog");
const filtersEl = document.querySelector("#filters");
const summaryEl = document.querySelector("#summary");
const queryEl = document.querySelector("#query");

const state = {
  category: "All",
  query: "",
  projects: [],
  categories: [],
};

function primaryUrl(project) {
  return project.github || project.gitlab;
}

function matches(project) {
  if (state.category !== "All" && project.category !== state.category) {
    return false;
  }
  const needle = state.query.trim().toLowerCase();
  if (!needle) return true;
  const haystack = [project.name, project.description, project.language, project.category]
    .join(" ")
    .toLowerCase();
  return haystack.includes(needle);
}

function formatUpdated(value) {
  if (!value) return "";
  const date = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

function link(href, label) {
  if (!href) return "";
  const a = document.createElement("a");
  a.href = href;
  a.textContent = label;
  return a;
}

function renderProject(project) {
  const article = document.createElement("article");
  article.className = "project";

  const body = document.createElement("div");
  const title = document.createElement("h3");
  const titleLink = document.createElement("a");
  titleLink.href = primaryUrl(project);
  titleLink.textContent = project.name;
  title.append(titleLink);
  const desc = document.createElement("p");
  desc.className = "desc";
  desc.textContent = project.description;

  const links = document.createElement("p");
  links.className = "links";
  for (const node of [
    link(project.github, "GitHub"),
    link(project.gitlab, "GitLab"),
    link(project.homepage, "Site"),
  ]) {
    if (node) links.append(node);
  }
  body.append(title, desc, links);

  const meta = document.createElement("div");
  if (project.language) {
    const lang = document.createElement("p");
    lang.className = "lang";
    lang.textContent = project.language;
    meta.append(lang);
  }
  const updated = formatUpdated(project.updated);
  if (updated) {
    const when = document.createElement("p");
    when.className = "updated";
    when.textContent = updated;
    meta.append(when);
  }

  article.append(body, meta);
  return article;
}

function render() {
  const visible = state.projects.filter(matches);
  catalogEl.replaceChildren();

  const groups =
    state.category === "All" && !state.query.trim()
      ? state.categories.filter((category) => visible.some((project) => project.category === category))
      : [null];

  if (!visible.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No projects match that search.";
    catalogEl.append(empty);
    return;
  }

  for (const category of groups) {
    const rows = category ? visible.filter((project) => project.category === category) : visible;
    if (category) {
      const section = document.createElement("section");
      section.className = "group";
      const heading = document.createElement("h2");
      heading.textContent = category;
      section.append(heading);
      catalogEl.append(section);
    }
    for (const project of rows) {
      catalogEl.append(renderProject(project));
    }
  }
}

function renderFilters() {
  const names = ["All", ...state.categories];
  filtersEl.replaceChildren();
  for (const name of names) {
    const button = document.createElement("button");
    button.type = "button";
    button.role = "tab";
    button.textContent = name;
    button.setAttribute("aria-selected", name === state.category ? "true" : "false");
    button.addEventListener("click", () => {
      state.category = name;
      for (const other of filtersEl.querySelectorAll("button")) {
        other.setAttribute("aria-selected", other === button ? "true" : "false");
      }
      render();
    });
    filtersEl.append(button);
  }
}

queryEl.addEventListener("input", () => {
  state.query = queryEl.value;
  render();
});

fetch("projects.json")
  .then((response) => {
    if (!response.ok) throw new Error(`catalog ${response.status}`);
    return response.json();
  })
  .then((data) => {
    state.projects = data.projects;
    state.categories = data.categories;
    const mirrors = data.projects.filter((project) => project.gitlab).length;
    summaryEl.textContent = `${data.projects.length} public original repositories. ${mirrors} have a public GitLab mirror. Forks are not listed.`;
    renderFilters();
    render();
  })
  .catch(() => {
    summaryEl.textContent = "The project index could not be loaded.";
  });
