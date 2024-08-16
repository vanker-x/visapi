import {defineConfig} from 'vitepress'
import {en} from './en.js'
import {zh} from './zh.js'
import {shared} from "./shared.js";

export default defineConfig({
    ...shared,
    locales: {
        root: {label: 'English', ...en},
        zh: {label: '简体中文', ...zh},
    }
})