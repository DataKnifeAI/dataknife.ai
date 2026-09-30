const recentEl = document.querySelector("#recent");

loadCatalog()
  .then((data) => {
    const recent = [...data.projects]
      .sort((a, b) => (b.updated || "").localeCompare(a.updated || ""))
      .slice(0, 6);
    recentEl.replaceChildren(...recent.map((project) => repoCard(project, { compact: true })));
  })
  .catch(() => {
    recentEl.replaceChildren(el("p", { class: "muted", text: "Recent activity could not be loaded." }));
  });
