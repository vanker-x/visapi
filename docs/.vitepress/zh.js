import {defineConfig} from 'vitepress'

export const zh = defineConfig({
    lang: 'zh-CN', themeConfig: {
        nav: nav(), sidebar: {
            "/zh/guide/": {base: "/zh/guide/", items: guideSideBar()},
            "/zh/advanced/": {base: "/zh/advanced/", items: advancedSideBar()},
        }
    }
})

function nav() {
    return [
        {
            text: '指南', link: '/zh/guide/installation', activeMatch: '/zh/guide/'
        }, {
            text: '进阶', link: '/zh/advanced/application', activeMatch: '/zh/advanced/'
        },
        {
            text: "API参考", link: '/zh/api-reference/application', activeMatch: '/zh/api-reference/'
        }
    ]
}

function guideSideBar() {
    return [{
        text: '指南', items: [
            {text: '安装', link: '/installation'},
            {
                text: "一些甜品", link: '/cakes/', collapsed: true, items: [
                    {
                        text: "规范", link: '/cakes/specification/', collapsed: true, items: [{
                            text: "RSGI", link: "/cakes/specification/RSGI",
                        }, {
                            text: "ASGI", link: "/cakes/specification/ASGI",
                        }, {
                            text: "WSGI", link: "/cakes/specification/WSGI",
                        },]
                    }, {text: "pydantic", link: '/cakes/pydantic'}, {text: "sqlalchemy", link: '/cakes/sqlalchemy'},]
            },
            {
                text: '部署',
                link: '/deployment/',
                collapsed: true,
                items: [{text: "granian", link: '/deployment/granian'}, {text: "uvicorn", link: '/deployment/uvicorn'},]
            },

        ]
    }]
}

function advancedSideBar() {
    return [
        {
            text: '进阶',
            collapsed: false,
            items: [{text: '应用', link: '/application'}, {text: '回调', link: '/callback'}, {
                text: '路由',
                link: '/routing/',
                collapsed: true,
                items: [{text: '路由器', link: '/routing/router'}, {
                    text: '路由', link: '/routing/route'
                }, {text: '路由转换器', link: '/routing/convertor'},

                ]
            }, {text: '配置', link: '/configuration'}, {text: '组', link: '/group'}, {
                text: '请求', link: '/request'
            }, {text: '响应', link: '/response'}, {
                text: '可视化', link: '/visualization'
            }, {text: 'Websocket', link: '/websocket'},]
        }
    ]
}