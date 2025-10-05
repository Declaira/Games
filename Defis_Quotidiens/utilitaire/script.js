let characters = [];
let selectedCharacter = null;
let attempts = [];

const input = document.getElementById('guessInput');
const suggestionsDiv = document.getElementById('suggestions');
const feedbackDiv = document.getElementById('feedback');
const attemptsDiv = document.getElementById('attempts');

let mode = "facile"; // "facile" ou "difficile"
const modeBtn = document.getElementById('modeBtn');

function loadCharacters(mode) {
  fetch("characters.json")
    .then(response => {
      if (!response.ok) throw new Error("Impossible de charger characters.json");
      return response.json();
    })
    .then(data => {
      // Filtre selon le mode
      if (mode === "facile") {
        characters = data.filter(char => char.height && char.height !== "Inconnue" && char.height.trim() !== "");
      } else {
        characters = data;
      }
      updateCharacterArcsByChapter(characters, arcsWithChapters);
      selectedCharacter = characters[Math.floor(Math.random() * characters.length)];
      attempts = [];
      attemptsDiv.innerHTML = "";
      feedbackDiv.textContent = "";
      input.value = "";
      input.style.display = 'block';
      input.disabled = false;
      suggestionsDiv.style.display = 'none';
      document.getElementById('victoryScreen').style.display = 'none';
      console.log("Personnage choisi :", selectedCharacter.name);
    })
    .catch(error => console.error("Erreur :", error));
}

function updateModeBtnStyle() {
  if (mode === "facile") {
    modeBtn.classList.remove("difficile");
    modeBtn.classList.add("facile");
  } else {
    modeBtn.classList.remove("facile");
    modeBtn.classList.add("difficile");
  }
  modeBtn.textContent = "Mode : " + (mode === "facile" ? "Facile" : "Difficile");
}

// Au chargement initial
updateModeBtnStyle();
loadCharacters(mode);

// Bouton pour changer de mode
modeBtn.addEventListener('click', () => {
  mode = mode === "facile" ? "difficile" : "facile";
  updateModeBtnStyle();
  loadCharacters(mode);
});


// === Liste des arcs avec chapitres ===
const arcsWithChapters = [
  { arc: "Romance Dawn", chapitre_debut: 1, chapitre_fin: 7 },
  { arc: "Ville d’Orange", chapitre_debut: 8, chapitre_fin: 21 },
  { arc: "Village de Syrup", chapitre_debut: 22, chapitre_fin: 41 },
  { arc: "Baratie", chapitre_debut: 42, chapitre_fin: 68 },
  { arc: "Arlong Park", chapitre_debut: 69, chapitre_fin: 95 },
  { arc: "Loguetown", chapitre_debut: 96, chapitre_fin: 100 },
  { arc: "Reverse Mountain", chapitre_debut: 101, chapitre_fin: 105 },
  { arc: "Whisky Peak", chapitre_debut: 106, chapitre_fin: 114 },
  { arc: "Little Garden", chapitre_debut: 115, chapitre_fin: 129 },
  { arc: "Drum", chapitre_debut: 130, chapitre_fin: 154 },
  { arc: "Alabasta", chapitre_debut: 155, chapitre_fin: 217 },
  { arc: "Jaya", chapitre_debut: 218, chapitre_fin: 236 },
  { arc: "Skypiea", chapitre_debut: 237, chapitre_fin: 302 },
  { arc: "Davy Back Fight", chapitre_debut: 303, chapitre_fin: 315 },
  { arc: "Water 7", chapitre_debut: 316, chapitre_fin: 374 },
  { arc: "Enies Lobby", chapitre_debut: 375, chapitre_fin: 430 },
  { arc: "Post-Enies Lobby", chapitre_debut: 431, chapitre_fin: 441 },
  { arc: "Thriller Bark", chapitre_debut: 442, chapitre_fin: 489 },
  { arc: "Archipel Sabaody", chapitre_debut: 490, chapitre_fin: 513 },
  { arc: "Amazon Lily", chapitre_debut: 514, chapitre_fin: 524 },
  { arc: "Impel Down", chapitre_debut: 525, chapitre_fin: 549 },
  { arc: "Marineford", chapitre_debut: 550, chapitre_fin: 580 },
  { arc: "Après-guerre", chapitre_debut: 581, chapitre_fin: 597 },
  { arc: "Île des Hommes-Poissons", chapitre_debut: 598, chapitre_fin: 653 },
  { arc: "Punk Hazard", chapitre_debut: 654, chapitre_fin: 699 },
  { arc: "Dressrosa", chapitre_debut: 700, chapitre_fin: 801 },
  { arc: "Zou", chapitre_debut: 802, chapitre_fin: 824 },
  { arc: "Whole Cake Island", chapitre_debut: 825, chapitre_fin: 902 },
  { arc: "Réverie", chapitre_debut: 903, chapitre_fin: 908 },
  { arc: "Pays des Wa", chapitre_debut: 909, chapitre_fin: 1057 },
  { arc: "Egghead", chapitre_debut: 1058, chapitre_fin: 1125 },
  { arc: "Erbaf", chapitre_debut: 1126, chapitre_fin: 1200 }
];

// Fonction qui met à jour le champ "arc" de chaque personnage selon son chapitre d'apparition
function updateCharacterArcsByChapter(characters, arcs) {
  characters.forEach(char => {
    const foundArc = arcs.find(a => 
      char.firstChapter >= a.chapitre_debut && char.firstChapter <= a.chapitre_fin
    );
    if (foundArc) {
      char.arc = foundArc.arc;
    } else {
      char.arc = "Inconnu";
    }
  });
}

// Mise à jour des arcs des personnages avant le jeu
updateCharacterArcsByChapter(characters, arcsWithChapters);

// === Liste ordonnée des arcs ===
const arcOrder = [
  "Romance Dawn", "Ville d’Orange", "Village de Syrup", "Baratie", "Arlong Park", "Loguetown",
  "Reverse Mountain", "Whisky Peak", "Little Garden", "Drum", "Alabasta", "Jaya", "Skypiea",
  "Davy Back Fight", "Water 7", "Enies Lobby", "Post-Enies Lobby", "Thriller Bark",
  "Archipel Sabaody", "Amazon Lily", "Impel Down", "Marineford", "Après-guerre",
  "Île des Hommes-Poissons", "Punk Hazard", "Dressrosa", "Zou", "Whole Cake Island",
  "Réverie", "Pays des Wa", "Egghead", "Erbaf"
];

// === Suggestions dynamiques ===
input.addEventListener('input', () => {
  const query = input.value.trim().toLowerCase();
  selectedIndex = -1;
  if (!query || characters.length === 0) {
    suggestionsDiv.style.display = 'none';
    return;
  }

  const filtered = characters
    .filter(c => {
      const nameParts = c.name.toLowerCase().split(' ');
      return nameParts.some(part => part.startsWith(query));
    })
    .slice(0, 10);

  if (filtered.length === 0) {
    suggestionsDiv.style.display = 'none';
    return;
  }

  suggestionsDiv.innerHTML = '';
  filtered.forEach(c => {
    const div = document.createElement('div');
    div.classList.add('suggestion-item');
    div.innerHTML = `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
      ">
        <img src="${c.image}" alt="${c.name}" style="
          width: 32px;
          height: 32px;
          border-radius: 50%;
          object-fit: cover;
        ">
        <span>${c.name}</span>
      </div>
    `;
    div.addEventListener('click', () => {
      handleGuess(c.name);
    });
    suggestionsDiv.appendChild(div);
  });

  suggestionsDiv.style.display = 'block';
  suggestionsDiv.scrollTop = 0; // Ajoute cette ligne pour remettre le slider en haut
});
// === Validation avec entrée clavier ===
let selectedIndex = -1;

input.addEventListener('keydown', (e) => {
  const items = suggestionsDiv.querySelectorAll('.suggestion-item');

  if (items.length === 0) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    selectedIndex = (selectedIndex + 1) % items.length;
    updateSelection(items);
  }

  if (e.key === 'ArrowUp') {
    e.preventDefault();
    selectedIndex = (selectedIndex - 1 + items.length) % items.length;
    updateSelection(items);
  }

  if (e.key === 'Enter') {
    e.preventDefault();
    if (selectedIndex >= 0 && selectedIndex < items.length) {
      items[selectedIndex].click();
    } else {
      handleGuess(input.value);
    }
  }
});

function updateSelection(items) {
  items.forEach((item, i) => {
    if (i === selectedIndex) {
      item.classList.add('selected');
      item.scrollIntoView({ block: "nearest" }); // optionnel
    } else {
      item.classList.remove('selected');
    }
  });
}

function handleGuess(guessText) {
  const guess = guessText.trim().toLowerCase();
  if (!guess) return;

  const guessedCharacter = characters.find(c => c.name.toLowerCase() === guess);
  if (!guessedCharacter) {
    feedbackDiv.textContent = "Personnage non trouvé, essaie encore.";
    return;
  }

  attempts.push(guessedCharacter);

  if (guessedCharacter.name === selectedCharacter.name) {
    feedbackDiv.textContent = "";
    afficherAttempts();
    setTimeout(() => {
      input.style.display = 'none';
      suggestionsDiv.style.display = 'none';
      const victoryScreen = document.getElementById('victoryScreen');
      const victoryImage = document.getElementById('victoryImage');
      const victoryName = document.getElementById('victoryName');
      victoryImage.src = selectedCharacter.image;
      victoryName.textContent = selectedCharacter.name;
      victoryScreen.style.display = 'block';
      input.disabled = true;
      // Ajout : change le message
      const gameMessage = document.getElementById('gameMessage');
      gameMessage.textContent = "Félicitation tu as trouvé !";
      gameMessage.classList.add("found");
    }, 200);
  } else {
    feedbackDiv.textContent = ""; // Retire le message "Raté !"
    afficherAttempts();
  }

  input.value = '';
  suggestionsDiv.style.display = 'none';
}


// === Règles de couleurs pour attributs textuels ===
function getColor(attr, guessValue, targetValue) {
  if (guessValue === targetValue) return "green";
  return "red";
}

// === Flèche pour Arc ===
function getArrow(guessedArc, targetArc) {
  const guessIndex = arcOrder.indexOf(guessedArc);
  const targetIndex = arcOrder.indexOf(targetArc);
  if (guessIndex === -1 || targetIndex === -1 || guessIndex === targetIndex) return "";
  return guessIndex < targetIndex ? " ↑" : " ↓";
}

// === Flèche pour valeurs numériques (height, bounty) ===
function getNumberArrow(guessValue, targetValue) {
  if (targetValue === "Inconnue" || !targetValue || guessValue === "Inconnue") return ""; // pas de comparaison
  if (guessValue === targetValue) return "";
  return guessValue < targetValue ? " ↑" : " ↓";
}

// === Couleur pour valeurs numériques ===
function getNumberColor(guessValue, targetValue) {
  if (guessValue === targetValue) return "green";
  return "red";
}

// === Affichage des essais ===
function afficherAttempts() {
  if (!document.getElementById("attemptsTable")) {
    attemptsDiv.innerHTML = `
      <h3>Vos essais :</h3>
      <table id="attemptsTable" style="border-collapse: collapse; width: 100%; text-align: center;">
        <thead>
          <tr>
            <th style="border: 1px solid #ccc; padding: 6px;">Image</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Genre</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Équipage</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Fruit</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Origine</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Arc</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Taille</th>
            <th style="border: 1px solid #ccc; padding: 6px;">Prime</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
        <div class="legend">
          <div class="legend-item">
            <span class="legend-box legend-correct"></span> Correct
          </div>
          <div class="legend-item">
            <span class="legend-box legend-wrong"></span> Incorrect
          </div>
          <div class="legend-item">
            <span class="legend-up"></span> Supérieur
          </div>
          <div class="legend-item">
            <span class="legend-down"></span> Inférieur
          </div>
        </div>
    `;
  }

function getArrowBackground(guessValue, targetValue, type = "number") {
  if (type === "arc") {
    const guessIndex = arcOrder.indexOf(guessValue);
    const targetIndex = arcOrder.indexOf(targetValue);
    if (guessIndex === -1 || targetIndex === -1 || guessIndex === targetIndex) return "";
    return guessIndex < targetIndex ? "images/arrow-up.png" : "images/arrow-down.png";
  } else {
    // type = "number" (taille, prime)
    if (targetValue === "Inconnue" || !targetValue || guessValue === "Inconnue") return "";
    if (guessValue === targetValue) return "";
    return guessValue < targetValue ? "images/arrow-up.png" : "images/arrow-down.png";
  }
}


  const tbody = document.querySelector("#attemptsTable tbody");
  const char = attempts[attempts.length - 1];

  const row = document.createElement("tr");

const cellContents = [
  {
    html: `<img src="${char.image}" alt="${char.name}" style="width:100%;height:100%;object-fit:cover;">`,
    bg: "white"
  },
  { html: char.gender, bg: getColor("gender", char.gender, selectedCharacter.gender) },
  { 
    html: char.affiliation === "" ? '<span style="color:black;">✖</span>' : char.affiliation, 
    bg: getColor("affiliation", char.affiliation, selectedCharacter.affiliation) 
  },
  { 
    html: char.dftype === "" ? '<span style="color:black;">✖</span>' : char.dftype, 
    bg: getColor("dftype", char.dftype, selectedCharacter.dftype) 
  },
  { html: char.origin, bg: getColor("origin", char.origin, selectedCharacter.origin) },
  { 
    html: `${char.arc}`, 
    bg: getColor("arc", char.arc, selectedCharacter.arc),
    arrow: getArrowBackground(char.arc, selectedCharacter.arc, "arc")
  },
  { 
    html: `${char.height}`, 
    bg: getNumberColor(char.height, selectedCharacter.height),
    arrow: getArrowBackground(char.height, selectedCharacter.height, "number")
  },
  { 
    html: `
      ${char.bounty.toLocaleString()} 
      <img src="images/berries.png" alt="Berry" class="berry-icon">
    `,
    bg: getNumberColor(char.bounty, selectedCharacter.bounty),
    arrow: getArrowBackground(char.bounty, selectedCharacter.bounty, "number")
  }
];

  cellContents.forEach(() => {
    const td = document.createElement("td");
    td.style.border = "1px solid #ccc";
    td.style.height = "50px";
    td.style.verticalAlign = "middle";
    td.style.textAlign = "center";
    row.appendChild(td);
  });

  tbody.insertBefore(row, tbody.firstChild);

cellContents.forEach((cell, i) => {
  setTimeout(() => {
    const td = row.children[i];
    td.style.transition = "transform 0.3s";
    td.style.transform = "rotateY(90deg)";
    setTimeout(() => {
      td.innerHTML = cell.html;

    if (cell.arrow) {
      td.style.backgroundImage = `url(${cell.arrow})`;
      td.style.backgroundSize = "100% 100%";   // 🟢 occupe toute la cellule
      td.style.backgroundPosition = "center";
      td.style.backgroundRepeat = "no-repeat";
    } else {
      td.style.background = cell.bg;
    }

      td.style.transform = "rotateY(0deg)";
    }, 300);
  }, i * 250);
});
}

// === Bouton rejouer ===
document.getElementById('replayBtn').addEventListener('click', () => {
  selectedCharacter = characters[Math.floor(Math.random() * characters.length)];
  attempts = [];
  attemptsDiv.innerHTML = "";
  feedbackDiv.textContent = "";
  input.value = "";
  input.style.display = 'block';
  input.disabled = false;
  suggestionsDiv.style.display = 'none';
  const victoryScreen = document.getElementById('victoryScreen');
  victoryScreen.style.display = 'none';
  // Ajout : remet le message initial
  const gameMessage = document.getElementById('gameMessage');
  gameMessage.textContent = "Devinez le personnage One Piece !";
  gameMessage.classList.remove("found");
  console.log("Nouveau personnage choisi :", selectedCharacter.name);
});
