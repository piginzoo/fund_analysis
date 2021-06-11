const App = {
    data() {
        return {
            command: "fund_analysis.analysis.calculate_alpha --code 009549 --type fund --period week --index 上证指数",
            image:'',
            result:'...',
            result_base64_images : []
        }
    },
    methods: {
        submit(event) {
            console.log("点击了提交，数据："+this.command)
            axios.post("/execute",{'command':this.command}).then((response) => {
                console.log("POST返回结果为："+response.data.result)
                console.log("图片："+response.data.images.length)
                this.result = response.data.result
                this.result_base64_images = response.data.images // base64 图片数组（多张）
            })
        }
    }
};
const app = Vue.createApp(App);
app.use(ElementPlus);
app.mount("#app");


