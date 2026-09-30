const LANGUAGE_COLORS = {
  Go: "#00add8",
  Python: "#3572a5",
  Rust: "#dea584",
  TypeScript: "#3178c6",
  JavaScript: "#f1e05a",
  Shell: "#89e051",
  HCL: "#844fba",
  HTML: "#e34c26",
  C: "#555555",
  "C++": "#f34b7d",
};

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) {
    if (child === null || child === undefined || child === "") continue;
    node.append(child);
  }
  return node;
}

function relativeDate(value) {
  if (!value) return "";
  const then = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(then.getTime())) return value;
  const days = Math.max(0, Math.round((Date.now() - then.getTime()) / 86400000));
  if (days === 0) return "Updated today";
  if (days === 1) return "Updated yesterday";
  if (days < 30) return `Updated ${days} days ago`;
  return `Updated ${new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" }).format(then)}`;
}

function languageBadge(language) {
  if (!language) return null;
  return el(
    "span",
    { class: "lang" },
    el("span", { class: "lang-dot", style: `background:${LANGUAGE_COLORS[language] || "#8b949e"}` }),
    language,
  );
}

function statusBadge(status) {
  if (!status) return null;
  return el("span", { class: `status status-${status.toLowerCase()}`, text: status });
}

function repoCard(project, { compact = false } = {}) {
  const primary = project.github || project.gitlab;
  const title = el(
    "h3",
    { class: "repo-name" },
    el("a", { href: primary, text: project.name }),
    el("span", { class: "visibility", text: "Public" }),
    statusBadge(project.status),
  );

  const topics =
    !compact && project.topics && project.topics.length
      ? el("p", { class: "topics" }, ...project.topics.slice(0, 6).map((topic) => el("span", { text: topic })))
      : null;

  const hosts = el(
    "span",
    { class: "hosts" },
    project.github ? el("a", { href: project.github, text: "GitHub" }) : null,
    project.gitlab ? el("a", { href: project.gitlab, text: "GitLab" }) : null,
    project.homepage ? el("a", { href: project.homepage, text: "Site" }) : null,
  );

  const meta = el(
    "p",
    { class: "repo-meta" },
    languageBadge(project.language),
    project.stars ? el("span", { text: `★ ${project.stars}` }) : null,
    el("span", { text: relativeDate(project.updated) }),
    hosts,
  );

  return el(
    compact ? "article" : "li",
    { class: compact ? "repo-card" : "repo-row" },
    title,
    el("p", { class: "repo-desc", text: project.description || "No description provided." }),
    topics,
    meta,
  );
}

function loadCatalog() {
  return fetch("projects.json").then((response) => {
    if (!response.ok) throw new Error(`catalog ${response.status}`);
    return response.json();
  });
}
