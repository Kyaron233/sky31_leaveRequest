// 事件委托：绑定两个选项框的点击事件
let dpOptions = document.querySelector('.department .options')
let ridOptions = document.querySelector('.role_in_depart .options')
// 定义函数处理选项
function check(ele, type) {
  // 获取选择结果
  let result = ele.innerText
  // 将选择结果展示到页面上
  let showEle = document.querySelector(`.${type}_name`)
  showEle.innerHTML = result
  // 修改页面字体颜色
  showEle.style.color = '#3A3A3A'
  // 将结果同步给接收数据的input标签
  let inputEle = document.querySelector(`input[name="${type}"]`)
  inputEle.value = ele.id
}
document.addEventListener('click', e => {
  let ele = e.target
  if (!dpOptions.classList.contains('hide')) {
    // 部门选项框显示期间
    // 点击选项框内部时选择后隐藏选项框
    if (ele.closest('.options')) check(ele, 'department')
    // 点击选项框外部时隐藏选项框
    dpOptions.classList.toggle('hide')
  } else if (!ridOptions.classList.contains('hide')) {
    // 职位选项框显示期间
    // 点击选项框内部时选择后隐藏选项框
    if (ele.closest('.options')) check(ele, 'role_in_depart')
    // 点击选项框外部时隐藏选项框
    ridOptions.classList.toggle('hide')
  } else if (ele.closest('.department')) {
    // 点击到部门一栏时改变选项框存在状态
    dpOptions.classList.toggle('hide')
  } else if (ele.closest('.role_in_depart')) {
    // 点击到职位一栏时改变选项框存在状态
    ridOptions.classList.toggle('hide')
  }
})

// 为输入框绑定输入事件，限制输入为数字或汉字
let inputs = document.querySelector('.message_items')
let inputLock = false
inputs.addEventListener('compositionstart', e => {
  // console.log(e.target.className)
  inputLock = true
})
inputs.addEventListener('compositionend', e => {
  let inputEle = e.target
  // console.log(e.target)
  inputLock = false
  if (inputEle.classList.contains('ch')) {
    // 解决其他语言输入法输入时的bug
    inputEle.value = inputEle.value.replace(/[^\u4E00-\u9FA5]/g, '')
  } else if (inputEle.classList.contains('num')) {
    // 解决限制输入数字时的bug
    inputEle.value = inputEle.value.replace(/[\D]/g, '')
  }
})
inputs.addEventListener('input', e => {
  let inputEle = e.target
  if (inputLock) return
  if (inputEle.classList.contains('ch')) {
    inputEle.value = inputEle.value.replace(/[^\u4E00-\u9FA5]/g, '')
  } else if (inputEle.classList.contains('num')) {
    inputEle.value = inputEle.value.replace(/[\D]/g, '')
  }
})

// 为添加按钮绑定点击事件
let addBtn = document.querySelector('.add_btn')
addBtn.addEventListener('click', () => {
  let memberForm = document.querySelector('.member_message_form')
  let formData = serialize(memberForm, { hash: true, empty: true })
  formData.role_in_depart = parseInt(formData.role_in_depart)
  console.log(formData)
  console.log(typeof formData.student_id)
  // 对获取到的信息进行判断
  if (!(formData.student_id.length === 12 && formData.tel.length === 11)) {
    popupTop.innerHTML = '添加失败'
    console.log(formData.student_id.length)
    console.log(formData.tel.length)
    popup.classList.remove('hide')
    return
  }
  console.log(formData)
  axios({
    method: 'post',
    url: '/add',
    data: {
      ...formData
    },
    withCredentials: true
  })
    .then(result => {
      console.log(result)
      // 添加成功弹窗
      popupTop.innerHTML = '添加成功'
      popup.classList.remove('hide')
      // 清空输入框
      document.querySelectorAll('.message_items input').forEach(item => (item.value = ''))
      let dpName = document.querySelector('.department_name')
      let ridName = document.querySelector('.role_in_depart_name')
      dpName.innerHTML = '请选择部门'
      dpName.style.color = '#A6A6A6'
      ridName.innerHTML = '请选择职位'
      ridName.style.color = '#A6A6A6'
    })
    .catch(error => {
      console.dir(error)
      popupTop.innerHTML = '添加失败'
      popup.classList.remove('hide')
    })
})
