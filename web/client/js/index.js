let options = document.querySelector('.options')
let select = document.querySelector('.select')
let departmentNameEle = document.querySelector('.department_name')
let departmentEle = document.querySelector('input[name="department"]')
let loginBtn = document.querySelector('.login')
let popup = document.querySelector('.popup_shadow')

// 选项框显示隐藏事件
function inputToggle() {
  options.classList.toggle('hide')
  popup.innerHTML = ''
  popup.classList.toggle('hide')
  document.body.classList.toggle('shadow')
}
window.addEventListener('click', e => {
  if (!options.classList.contains('hide')) {
    // 选项框显示期间，点击到选项框外部时隐藏选项框，同时去除页面阴影
    inputToggle()
  } else if (e.target === select || e.target.nodeName === 'SPAN') {
    // 选项框未显示时，点击到“部门”一栏时显示选项框，同时为页面添加阴影
    inputToggle()
  }
})
// 阻止事件流，防止点击选项框内部时隐藏
options.addEventListener('click', e => {
  e.stopPropagation()
})

// 选择部门
function check(e) {
  // 获取选择部门结果
  let departmentName = e.target.innerText
  // 将结果展示到页面上
  departmentNameEle.innerHTML = departmentName
  departmentNameEle.style.color = '#3A3A3A'
  // 将结果同步给接收数据的input标签
  departmentEle.value = departmentName
  // 隐藏选项框并移除页面阴影
  inputToggle()
}

// 绑定登录事件
loginBtn.addEventListener('click', () => {
  // 获取表单数据
  let userForm = document.querySelector('.user_form')
  let userData = serialize(userForm, { hash: true, empty: true })
  console.log(userData)
  if (!userData.department || !userData.student_id || !userData.password) {
    popup.innerHTML = `<div class="popup">
    <div class="top">输入错误！</div>
    <div class="bottom">
      <button class="close">确定</button>
    </div>
    </div>`
    popup.classList.remove('hide')
    return
  }
  // 向服务器提交数据并获取登录许可
  axios({
    method: 'post',
    url: '/login',
    data: userData,
    withCredentials: true
  })
    .then(result => {
      console.log(result)
      // 保存部门身份
      localStorage.setItem('department', result.data.department)
      localStorage.setItem('departmentName', result.data.department_name)
      // 登录成功跳转到主页
      location.href = './page/homepage.html'
    })
    .catch(error => {
      console.dir(error)
      // 登录失败，弹框提示
      popup.innerHTML = `<div class="popup">
                          <div class="top">输入错误！</div>
                          <div class="bottom">
                            <button class="close">确定</button>
                          </div>
                        </div>`
      popup.classList.remove('hide')
    })
})

// 绑定弹框消失事件
popup.addEventListener('click', e => {
  if (e.target.classList.contains('close')) {
    popup.classList.add('hide')
  }
})
