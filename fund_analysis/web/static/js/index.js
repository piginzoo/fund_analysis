const App = {
    data() {
        return {
            command: "--code 009549 --type fund --period week --index 上证指数",
            image:'',
            result:'...',
            result_base64_images : [],
            calculator:'',
            calculators:[],
            help:'命令帮助?'
        }
    },
    mounted() {
            axios.post("/list").then((response) => {
                console.log("POST返回结果为："+response.data.list)
                this.calculators = response.data.list
            })
    },
    methods: {
        submit(event) {
            console.log("点击了提交，数据："+this.command)
            axios.post("/execute",{'calculator':this.calculator, 'command':this.command}).then((response) => {
                console.log("POST返回结果为："+response.data.result)
                console.log("图片："+response.data.images.length)
                this.result = response.data.result
                this.result_base64_images = response.data.images // base64 图片数组（多张）
            })
        },
        select_calculator(item){
            console.log("选中："+item)
            axios.post("/help",{'name':item}).then((response) => {
                console.log("POST返回结果为：["+response.data.help+"]")
                this.help = response.data.help
                this.calculator = item
                this.command=''
                this.result=''
                this.result_base64_images=[]
            })

        }
    }
};
const app = Vue.createApp(App);
app.use(ElementPlus);
app.mount("#app");


