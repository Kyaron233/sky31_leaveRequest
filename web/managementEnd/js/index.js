// 绑定登录事件
let loginBtn = document.querySelector('.login_btn')
let popup = document.querySelector('.popup_shadow')
loginBtn.addEventListener('click', () => {
  // 获取表单数据并提交
  let loginForm = document.querySelector('.user_form')
  let formData = serialize(loginForm, { hash: true, empty: true })
  console.log(formData)
  // 将数据提交给服务器并获取登录状态
  axios({
    method: 'post',
    url: '/login',
    data: formData,
    withCredentials: true
  })
    .then(result => {
      console.log(result)
      // 登录成功跳转到主页
      location.href = './page/homepage.html'
    })
    .catch(error => {
      console.dir(error)
      // 登录失败，弹框提示
      popup.classList.remove('hide')
    })
})

// 绑定弹框消失事件
document.querySelector('.popup .bottom').addEventListener('click', () => {
  popup.classList.add('hide')
})
