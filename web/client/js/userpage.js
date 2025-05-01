let userDataPage = document.querySelector('.user_data_content')
let modifyPwdPage = document.querySelector('.modify_password_content')
let departmentName = document.querySelector('header h1')

let popup = document.querySelector('.popup_shadow')
let popupTop = popup.querySelector('.top')

let nameEle = document.querySelector('.name')
let departmentEle = document.querySelector('.department')
let stuIdEle = document.querySelector('.stu_id')

let departmentNames = document.querySelectorAll('h1')
departmentNames.forEach(departmentName => {
  departmentName.innerHTML = localStorage.getItem('departmentName')
})
// 根据 URL 选择展示页面
if (location.href.split('#')[1]) {
  // 展示修改密码页
  modifyPwdPage.classList.remove('hide')
  userDataPage.classList.add('hide')
} else {
  // 展示用户信息页
  userDataPage.classList.remove('hide')
  modifyPwdPage.classList.add('hide')
}

// 获取用户信息并展示到页面上
axios({
  method: 'get',
  url: '/info'
})
  .then(result => {
    console.log(result)
    departmentName.innerHTML = result.data.department
    nameEle.innerHTML = result.data.name
    departmentEle.innerHTML = result.data.department
    stuIdEle.innerHTML = result.data.student_id
  })
  .catch(err => {
    console.dir(err)
  })

// 点击“修改密码”

// 监听到页面url发生变化时
window.addEventListener('popstate', () => {
  // 确保展示到正确的页面上
  pageUrl = location.href.split('#')[1]
  if (pageUrl) {
    // 展示修改密码页
    modifyPwdPage.classList.remove('hide')
    userDataPage.classList.add('hide')
  } else {
    // 展示用户信息页
    userDataPage.classList.remove('hide')
    modifyPwdPage.classList.add('hide')
  }
  // 展示到对应页面时执行相应操作
})

// 点击“确认”移除提示框
popup.querySelector('.bottom').addEventListener('click', () => {
  popup.classList.add('hide')
})
