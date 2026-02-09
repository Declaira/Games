window.injectHeader = function(options = {}) {
  const {
    title = "Déclaira",
    homeLink = "accueil.html",
    showHome = true,
    homeIcon = "🏠", // Paramètre icône accueil
    autoHide = false, // Paramètre logique de masquage
    customBackground = "linear-gradient(to right, #ff9a00, #ff4e00)", // Paramètre fond
    logoUrl = "" // Paramètre image titre
  } = options;

  const style = `
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@600;700&display=swap');
    
    body {
      transition: padding-top 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      margin: 0;
      padding-top: ${autoHide ? '0' : '100px'};
    }

    header {
      background: ${customBackground};
      color: white; 
      height: 100px; 
      position: fixed; /* Fixé pour permettre le masquage */
      top: 0; left: 0; width: 100%;
      font-family: 'Quicksand', sans-serif;
      display: flex; justify-content: center; align-items: center;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
      z-index: 9999;
      transform: translateY(${autoHide ? '-100%' : '0'}); 
      transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    header.header-visible { transform: translateY(0); }

    .header-title { font-size: 2.2em; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    .header-logo { max-height: 70px; max-width: 250px; object-fit: contain; }

    .home-icon { 
      position: absolute; left: 20px; 
      width: 48px; height: 48px; 
      background: white; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 24px; text-decoration: none;
      border: 2px solid rgba(255,255,255,0.5);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      transition: transform 0.2s ease;
      cursor: pointer;
    }
    .home-icon:hover { transform: scale(1.15); }

    .user-profile-widget {
      position: absolute; right: 20px; display: flex; align-items: center;
      gap: 12px; cursor: pointer; padding: 5px 10px; border-radius: 30px;
    }

    .user-avatar-circle {
      width: 48px; height: 48px; background: white; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 24px; border: 2px solid rgba(255,255,255,0.5);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1); overflow: hidden;
      transition: transform 0.2s ease;
    }
    /* Agrandissement du rond de l'avatar au survol du widget */
    .user-profile-widget:hover .user-avatar-circle { transform: scale(1.15); }
    
    .user-avatar-circle img { width: 100%; height: 100%; object-fit: cover; }

    .user-info-text { display: none; flex-direction: column; text-align: right; }
    @media (min-width: 600px) { .user-info-text { display: flex; } }
    .user-name { font-weight: bold; font-size: 0.95em; }

    .profile-dropdown {
      position: absolute; top: 75px; right: 0; background: white; color: #333;
      border-radius: 12px; width: 210px; box-shadow: 0 8px 20px rgba(0,0,0,0.15);
      display: none; flex-direction: column; padding: 8px 0; z-index: 1100;
    }
    .profile-dropdown.show { display: flex; animation: fadeInMenu 0.2s ease-out; }

    @keyframes fadeInMenu {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .dropdown-item {
      padding: 12px 20px; border: none; background: none; text-align: left;
      font-family: inherit; font-size: 0.95em; cursor: pointer;
      display: flex; align-items: center; gap: 10px; color: #2c3e50; width: 100%;
    }
    .dropdown-item:hover { background: #f8f9fa; color: #ff4e00; }
    .dropdown-divider { height: 1px; background: #eee; margin: 5px 0; }
    .hidden { display: none !important; }
  </style>
  `;

  const loginPath = homeLink.replace('accueil.html', 'login.html');
  const comptePath = homeLink.replace('accueil.html', 'compte.html');

  document.write(`
    ${style}
    <header id="main-header">
      ${showHome ? `<a href="${homeLink}" class="home-icon">${homeIcon}</a>` : ""}
      
      ${logoUrl ? `<img src="${logoUrl}" alt="${title}" class="header-logo">` : `<span class="header-title">${title}</span>`}

      <div class="user-profile-widget" id="header-profile-trigger">
        <div class="user-info-text">
          <span class="user-name" id="header-username">Chargement...</span>
        </div>
        <div class="user-avatar-circle" id="header-avatar">👤</div>

        <div class="profile-dropdown" id="header-dropdown">
          <div id="menu-logged-in" class="hidden">
            <button class="dropdown-item" onclick="window.location.href='${comptePath}'">⚙️ Mon Compte</button>
            <button class="dropdown-item" onclick="window.location.href='${loginPath}'">🔄 Changer de profil</button>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item" id="header-logout-btn" style="color: #e74c3c;">🚪 Déconnexion</button>
          </div>
          <div id="menu-guest" class="hidden">
            <button class="dropdown-item" id="btn-goto-login">🔑 Se connecter</button>
            <button class="dropdown-item" id="btn-goto-signup">✨ Créer un compte</button>
          </div>
        </div>
      </div>
    </header>
    
    <script type="module">
      import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
      import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth.js";
      import { getDatabase, ref, get } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-database.js";

      const firebaseConfig = {
        apiKey: "AIzaSyB29fMpTwBgsqkjijkNoQJ2kGChSeQDX_w",
        authDomain: "quiz-ea203.firebaseapp.com",
        databaseURL: "https://quiz-ea203-default-rtdb.europe-west1.firebasedatabase.app",
        projectId: "quiz-ea203",
        storageBucket: "quiz-ea203.firebasestorage.app",
        messagingSenderId: "605137421110",
        appId: "1:605137421110:web:289e0876fe06108deaa997"
      };

      const app = initializeApp(firebaseConfig);
      const auth = getAuth(app);
      const db = getDatabase(app);

      const header = document.getElementById('main-header');
      const trigger = document.getElementById('header-profile-trigger');
      const dropdown = document.getElementById('header-dropdown');
      const nameEl = document.getElementById('header-username');
      const avatarEl = document.getElementById('header-avatar');
      const loggedInMenu = document.getElementById('menu-logged-in');
      const guestMenu = document.getElementById('menu-guest');
      const body = document.body;

      // --- LOGIQUE VISUELLE (Masquage) ---
      if (${autoHide}) {
        const showH = () => { header.classList.add('header-visible'); body.style.paddingTop = "100px"; };
        const hideH = () => { if (!dropdown.classList.contains('show')) { header.classList.remove('header-visible'); body.style.paddingTop = "0px"; }};

        document.addEventListener('mousemove', (e) => {
          if (e.clientY < 60) showH();
          else if (e.clientY > 110) hideH();
        });

        let lastS = window.pageYOffset;
        window.addEventListener('scroll', () => {
          let currS = window.pageYOffset;
          if (currS < lastS && currS > 50) showH();
          else if (currS > lastS && currS > 100) hideH();
          lastS = currS;
        });
      }

      // Gestion du menu déroulant
      trigger.onclick = (e) => { e.stopPropagation(); dropdown.classList.toggle('show'); };
      document.addEventListener('click', () => dropdown.classList.remove('show'));

      // Redirections mode Guest
      document.getElementById('btn-goto-login').onclick = () => { window.location.href = "${loginPath}?mode=login"; };
      document.getElementById('btn-goto-signup').onclick = () => { window.location.href = "${loginPath}?mode=signup"; };

      // --- AUTHENTIFICATION ---
      onAuthStateChanged(auth, async (user) => {
        const savedUid = localStorage.getItem('active_uid');
        const uidToFetch = savedUid || (user ? user.uid : null);

        if (uidToFetch) {
          const snapshot = await get(ref(db, 'users/' + uidToFetch));
          if (snapshot.exists()) {
            const data = snapshot.val();
            nameEl.textContent = data.username || "Joueur";
            if (data.avatar && data.avatar.length > 5) {
                if(data.avatar.startsWith('data:image') || data.avatar.startsWith('http')) {
                    avatarEl.innerHTML = '<img src="' + data.avatar + '">';
                } else {
                    avatarEl.textContent = data.avatar;
                }
            } else {
                avatarEl.innerHTML = "👤";
            }
            loggedInMenu.classList.remove('hidden');
            guestMenu.classList.add('hidden');
            return; 
          }
        }
        nameEl.textContent = "Invité";
        avatarEl.innerHTML = "👤";
        loggedInMenu.classList.add('hidden');
        guestMenu.classList.remove('hidden');
      });

      const logoutBtn = document.getElementById('header-logout-btn');
      if(logoutBtn) {
        logoutBtn.onclick = () => {
          signOut(auth).then(() => {
            localStorage.removeItem('active_uid');
            window.location.href = "${loginPath}";
          });
        };
      }
    </script>
  `);
}