import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import AiToolbar from './components/ai-toolbar.vue'

loadFonts()

createApp(App)
  .component('ai-toolbar', AiToolbar)
  .use(vuetify)
  .mount('#app')