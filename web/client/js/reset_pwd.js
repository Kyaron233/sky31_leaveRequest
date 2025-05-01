let submitBtn = document.querySelector('.submit')
let popup = document.querySelector('.popup_shadow')
let popTop = document.querySelector('.popup .top')
let popBottom = document.querySelector('.popup .bottom')
submitBtn.addEventListener('click', () => {
  // 获取用户填写的信息
  let userForm = document.querySelector('.user_form')
  let userData = serialize(userForm, { hash: true, empty: true })
  // 向服务器提交数据并获取重置状态
  axios({
    method: 'post',
    url: '/forget_pswd',
    data: userData
  })
    .then(result => {
      console.log(result)
      popTop.innerHTML = `验证成功<br/>密码已重置为<br/>${1}`
      popBottom.innerHTML = '返回登录页面'
      popup.classList.remove('hide')
      popBottom.addEventListener('click', () => {
        location.href = '../index.html'
      })
    })
    .catch(error => {
      console.dir(error)
      popTop.innerHTML = '输入错误'
      popBottom.innerHTML = '确定'
      popup.classList.remove('hide')
      popBottom.addEventListener('click', () => {
        popup.classList.add('hide')
      })
    })
})
