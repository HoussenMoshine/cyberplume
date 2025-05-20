// Styles
import '@mdi/font/css/materialdesignicons.css' // Nous garderons MDI pour l'instant, Tabler sera intégré via composants
import 'vuetify/styles'

// Vuetify
import { createVuetify } from 'vuetify'

// Thème personnalisé CyberPlume
const cyberPlumeTheme = {
  dark: false, // Pour l'instant, nous définissons uniquement le thème clair
  colors: {
    background: '#F8F6F0', // Fond Principal (Blanc cassé/Crème)
    surface: '#FFFFFF', // Fond des éléments surélevés (cartes, menus) - Gardons blanc pour contraste initial
    'surface-variant': '#B0D7E5', // Fond Secondaire / Cartes (Bleu ciel clair) - Peut être utilisé pour des surfaces alternatives
    primary: '#4DB1AB', // Primaire (Bleu-vert moyen)
    'primary-darken-1': '#3E9A94', // Variation plus foncée si besoin
    secondary: '#3B79B8', // Secondaire / Accent Fort (Bleu moyen)
    'secondary-darken-1': '#30669A', // Variation plus foncée si besoin
    error: '#EF5350', // Rouge doux
    info: '#3B79B8', // Utilisation du secondaire pour info
    success: '#66BB6A', // Vert doux
    warning: '#FFCA28', // Ambre doux

    // Couleurs de texte (Vuetify les gère souvent implicitement, mais on peut les forcer si besoin)
    'on-background': '#333333', // Texte sur fond principal
    'on-surface': '#333333', // Texte sur surface (cartes, etc.)
    'on-primary': '#FFFFFF', // Texte sur couleur primaire
    'on-secondary': '#FFFFFF', // Texte sur couleur secondaire
    'on-error': '#FFFFFF',
    'on-success': '#FFFFFF',
    'on-warning': '#333333', // Texte foncé sur avertissement (jaune)
  },
  variables: {
    // Configuration de la typographie globale via variables CSS
    'font-family-base': "'Lato', sans-serif", // Police pour le corps de texte
    'font-family-headings': "'Merriweather', serif", // Police pour les titres

    // Ajustement potentiel des tailles de police de base (optionnel, peut être fait en CSS global aussi)
    // 'font-size-root': '16px', // Taille de base (rem)

    // Ajustement des arrondis (optionnel, pour cohérence)
    'border-radius-root': '6px', // Rayon de bordure global pour les composants
  }
}

export default createVuetify({
  theme: {
    defaultTheme: 'cyberPlumeTheme', // Utiliser notre thème personnalisé
    themes: {
      cyberPlumeTheme, // Enregistrer notre thème
    },
  },
  // Configuration globale des composants
  defaults: {
    VCard: {
      elevation: 2, // Ajoute une ombre subtile par défaut
      rounded: 'lg', // Applique des coins arrondis larges par défaut
      // color: 'surface-variant' // ANNULÉ: On revient au fond 'surface' (blanc) par défaut pour une meilleure lisibilité
    },
    VBtn: {
      rounded: 'lg', // Applique les mêmes coins arrondis que les cartes
      style: { textTransform: 'none', letterSpacing: 'normal' } // Désactive les majuscules et ajuste l'espacement
    },
    VDialog: {
      rounded: 'lg' // Applique les mêmes coins arrondis aux boîtes de dialogue
      // Le fond par défaut sera 'surface' (blanc), ce qui est correct pour la lisibilité
    },
    VList: {
      density: 'compact', // Rend les listes plus compactes par défaut
      // bgColor: 'transparent' // Assure un fond transparent par défaut pour mieux s'intégrer (COMMENTÉ POUR DEBUG TRANSPARENCE)
    },
    VListItem: {
      rounded: 'lg' // Applique les mêmes coins arrondis lors du survol/sélection pour cohérence
    },
    VTextField: {
      variant: 'outlined',
      density: 'compact',
      color: 'primary', // Utilise la couleur primaire pour l'accentuation
      rounded: 'lg' // Applique les mêmes coins arrondis pour cohérence
    },
    VSelect: {
      variant: 'outlined',
      density: 'compact',
      color: 'primary',
      rounded: 'lg' // Applique les mêmes coins arrondis pour cohérence
    },
    VTextarea: {
      variant: 'outlined',
      density: 'compact',
      color: 'primary',
      rounded: 'lg' // Applique les mêmes coins arrondis pour cohérence
    },
    VChip: {
      rounded: 'lg' // Applique les mêmes coins arrondis aux puces
    }
  }
})