import {defineConfig} from 'vitepress'

export const en = defineConfig({
    lang: 'en-US',
    themeConfig: {
        nav: nav()

    }
})

function nav() {
    return [
        {
            text: 'Guide',
            link: '/en/guide/installation',
            activeMatch: '/guide/'
        },
    ]
}