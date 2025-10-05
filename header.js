function injectHeader(options = {}) {
  const {
    logo = null,        // URL de l'image du logo
    title = "Déclaira", // texte du titre si pas d'image
    homeLink = "accueil.html",
    showHome = true,
    modeBtn = null      // texte du bouton mode ou null si absent
  } = options;

  const style = `
  <style>
    @keyframes slideFadeIn {
      0% { opacity: 0; transform: translateY(-20px); }
      100% { opacity: 1; transform: translateY(0); }
    }

    header {
      background: linear-gradient(to right, #ff9a00, #ff4e00);
      color: white;
      height: 100px;
      position: relative;
      font-family: 'Quicksand', sans-serif;
      animation: slideFadeIn 0.8s ease-out;
      display: flex;
      justify-content: center;  /* centre le contenu principal */
      align-items: center;
    }

    .header-logo {
      max-height: 100%;
      height: auto;
      display: block;
    }

    .header-title {
      font-size: 2.5em;
      font-weight: bold;
      color: white;
    }

    .home-icon {
      position: absolute;
      left: 20px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 2.5em;
      text-decoration: none;
      color: white;
    }

    .home-icon:hover {
      color: #f1f1f1;
    }

    .mode-btn {
      position: absolute;
      right: 20px;
      top: 50%;
      transform: translateY(-50%);
      padding: 8px 18px;
      font-size: 16px;
      border-radius: 8px;
      background: #38d46a;
      color: #fff;
      border: 2px solid #fff;
      cursor: pointer;
      font-family: 'Quicksand', sans-serif;
      transition: background 0.3s, transform 0.2s;
    }

    .mode-btn:hover {
      background: #2ecc71;
      transform: scale(1.05);
    }
  </style>
  `;

  const homeIcon = showHome
    ? `<a href="${homeLink}" class="home-icon">🏠</a>`
    : "";

  const content = logo
    ? `<img src="${logo}" alt="Logo" class="header-logo">`
    : `<span class="header-title">${title}</span>`;

  const modeButtonHTML = modeBtn
    ? `<button class="mode-btn">${modeBtn}</button>`
    : "";

  document.write(`
    ${style}
    <header>
      ${homeIcon}
      ${content}
      ${modeButtonHTML}
    </header>
  `);
}
