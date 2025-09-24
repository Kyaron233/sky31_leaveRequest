// axios 公共配置
// 基地址
// axios.defaults.baseURL = 'http://blog.ruarua.site:8000'
axios.defaults.baseURL = '/admin'

// 添加请求拦截器
axios.interceptors.request.use(
  function (config) {
    // 在发送请求之前做些什么
    return config
  },
  function (error) {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  function (response) {
    // 2xx 范围内的状态码都会触发该函数
    // 对响应数据做点什么
    // const result = response.data
    return response
  },
  function (error) {
    // 超出 2xx 范围的状态码都会触发该函数
    // 对响应错误做点什么，例如：统一对 401 身份验证失败情况做出处理
    // console.dir(error)
    if (error?.response?.status === 401) {
      if (location.href.endsWith('index.html') || location.href.endsWith('/')) {
        alert(`${error.response.data.message} 请重新登录!`)
        return Promise.reject(error)
      }
      // 清除缓存
      localStorage.clear()
      // 跳转到登录页面
      window.location.href = '../index.html'
      return Promise.reject(error)
    }
    return Promise.reject(error)
  }
)
