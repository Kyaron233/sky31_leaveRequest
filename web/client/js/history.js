let formList = document.querySelector('.form_list')
let requestForm = document.querySelector('.request_form')
let popup = document.querySelector('.popup')
let popupTop = document.querySelector('.popup .top')

let activityItems = document.querySelector('.activity_items')

// 部门名称
let departmentNames = document.querySelectorAll('h1')
departmentNames.forEach(departmentName => {
  departmentName.innerHTML = localStorage.getItem('departmentName')
})
// 发送请求，获取数据并渲染到页面
axios({
  method: 'get',
  url: '/query/history/self'
})
  .then(result => {
    console.log(result)
    let data = result.data

    // 先清空页面
    activityItems.innerHTML = ''
    data?.forEach(requestFormData => {
      let li = document.createElement('li')
      li.id = requestFormData.whoLeave_event_id
      li.classList.add('item')
      let approved = '未审批'
      if (requestFormData.is_permitted === 1) {
        approved = '同&nbsp;&nbsp;&nbsp;&nbsp;意'
        li.classList.add('approved')
        li.classList.add('agree')
      } else if (requestFormData.is_permitted === -1) {
        approved = '不同意'
        li.classList.add('approved')
        li.classList.add('disagree')
      }
      li.innerHTML = `
      <div class="activity_name">${requestFormData.whoLeave_event}</div>
      <div class="approval_status">${approved}</div>
      <button class="cancel">撤销</button>
      <button class="details">详情</button>
    `
      activityItems.appendChild(li)
    })
    if (activityItems.querySelectorAll('li').length > 0) {
      document.querySelector('.form_list section').style.backgroundImage = 'none'
    }
  })
  .catch(error => {
    console.dir(error)
  })

// 根据 URL 选择展示页面
if (location.href.split('#')[1]) {
  // 展示请假单
  formList.classList.add('hide')
  requestForm.classList.remove('hide')
} else {
  // 展示列表
  formList.classList.remove('hide')
  requestForm.classList.add('hide')
}

// 事件委托：为撤销和详情按钮绑定点击事件
let userName = document.querySelector('input[name="user_name"]')
let userId = document.querySelector('input[name="stu_id"]')
let reason = document.querySelector('textarea')
let imagesEle = document.querySelector('.images')
activityItems.addEventListener('click', e => {
  let target = e.target
  let id = target.closest('li').id

  if (target.classList.contains('cancel')) {
    // 撤销事件
    // 若申请已批准，不做任何操作
    if (target.parentElement.classList.contains('approved')) return
    // 若申请未批准，撤销此条请假记录
    revoke(id)
  } else if (target.classList.contains('details')) {
    // 详情事件
    // 跳转到请假申请详情页
    let activityName = target.closest('.item').querySelector('.activity_name').innerHTML
    console.log(id)
    userName.value = ''
    userId.value = ''
    reason.value = ''
    imagesEle.innerHTML = ''
    axios({
      method: 'get',
      url: `/main/leaveRequest/${id}`
    })
      .then(result => {
        console.log(result.data)
        if (result.data.message) return
        let data = result.data
        userName.value = data.whoLeave_name
        userId.value = data.whoLeave_id
        reason.value = data.whoLeave_reason
        Object.keys(data.whoLeave_photo).forEach(base64String => {
          let newImgEle = document.createElement('div')
          newImgEle.classList.add('image_ele')
          newImgEle.innerHTML = `<span class="delete" --url="${data.whoLeave_photo[base64String]}">×</span><img src="${data.whoLeave_photo[base64String]}" alt="" />`
          imagesEle.appendChild(newImgEle)
        })
      })
      .catch(error => {
        console.dir(error)
      })
    location.href = location.href + '#details?activity=' + activityName
  }
})

// 监听到页面url发生变化时
window.addEventListener('popstate', () => {
  // 确保展示到正确的页面上
  pageUrl = location.href.split('#')[1]
  if (pageUrl) {
    // 展示请假单
    formList.classList.add('hide')
    requestForm.classList.remove('hide')
  } else {
    // 展示列表
    formList.classList.remove('hide')
    requestForm.classList.add('hide')
  }
  // 展示到对应页面时执行相应操作
})

// 点击按钮返回
let backBtn = document.querySelector('.back')
backBtn.addEventListener('click', () => {
  // 跳转到上一页
  // location.href = location.href.split('#')[0]
  history.back()
})

// 点击“确认”移除提示框
popup.querySelector('.bottom').addEventListener('click', () => {
  popup.classList.add('hide')
})
