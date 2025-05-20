/**
 * plugins/webfontloader.js
 *
 * webfontloader documentation: https://github.com/typekit/webfontloader
 */

export async function loadFonts () {
  const webFontLoader = await import('webfontloader')

  webFontLoader.load({
    google: {
      // Charger Lato pour le corps de texte (plusieurs graisses)
      // Charger Merriweather pour les titres (standard et bold)
      families: [
        'Lato:300,400,700&display=swap',
        'Merriweather:400,700&display=swap'
      ],
    },
  })
}