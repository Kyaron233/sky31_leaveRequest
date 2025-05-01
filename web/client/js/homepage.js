let formList = document.querySelector('.form_list')
let requestForm = document.querySelector('.request_form')
// let departmentName = formList.querySelector('.department_name')
let activityItems = document.querySelector('.activity_items')

let userName = document.querySelector('input[name="user_name"]')
let leaveReason = document.querySelector('textarea[name="reason"]')
let imagesEle = document.querySelector('.images')

let departmentNames = document.querySelectorAll('h1')
departmentNames.forEach(departmentName => {
  departmentName.innerHTML = localStorage.getItem('departmentName')
})

// 发送请求，获取数据并渲染到页面
axios({
  url: '/main',
  method: 'get'
})
  .then(result => {
    console.log(result)
    let activityDatas = result.data
    activityDatas?.forEach(activityData => {
      let date = new Date(activityData.event_date)
      // 转换时间格式
      const formattedDate = date.toISOString().split('T')[0].split('-').join('.')

      let item = document.createElement('li')
      item.classList.add('item')
      item.id = activityData.event_id
      item.innerHTML = `<div class="activity_name">${activityData.event_name}</div>
        <div class="expiration_date"><span class="date">${formattedDate}</span><span>（截止时间）</span></div>
      `
      // 若需要证明材料，添加 photo_needed 类名
      if (activityData.is_photo_needed === 1) {
        item.classList.add('photo_needed')
      }
      // 若活动已结束，添加 ended 类名
      if (!activityData.isActive) {
        item.classList.add('ended')
      }

      activityItems.appendChild(item)
    })
    // 若有内容则隐藏背景图
    if (activityItems.querySelectorAll('.item').length != 0) {
      document.querySelector('.form_list section').style.backgroundImage = 'none'
    }
  })
  .catch(error => {
    console.dir(error)
  })

function is_photo_needed() {
  let isPhoto = location.href.split('&')[0].split('=')[1]
  if (isPhoto === 'true') {
    document.querySelector('.photo').classList.remove('hide')
  } else {
    document.querySelector('.photo').classList.add('hide')
  }
}

// 若已有填写数据则展示到页面
function getData(id) {
  userName.value = ''
  leaveReason.value = ''
  imagesEle.innerHTML = `<div class="add_image">
                        + 添加图片
                        <br />
                        <span>图片要求：最多三张</span>
                      </div>`
  axios({
    method: 'get',
    url: `/main/leaveRequest/${id}`
  })
    .then(result => {
      console.log(result.data)
      if (result.data.message) return
      let data = result.data
      userName.value = data.whoLeave_name
      leaveReason.value = data.whoLeave_reason
      Object.keys(data.whoLeave_photo).forEach(base64String => {
        console.log(base64String)
        console.log()
        let newImgEle = document.createElement('div')
        newImgEle.classList.add('image_ele')
        newImgEle.innerHTML = `<span class="delete" --url="${data.whoLeave_photo[base64String]}">×</span><img src="${data.whoLeave_photo[base64String]}" alt="" />`
        imagesEle.insertBefore(newImgEle, addImageBtn)
      })
    })
    .catch(error => {
      console.dir(error)
    })
}

// 根据 URL 选择展示页面
if (location.href.split('#')[1]) {
  // 展示请假单
  requestForm.classList.remove('hide')
  is_photo_needed()
  let id = location.href.split('=').splice(-1)[0]
  getData(id)
  formList.classList.add('hide')
} else {
  // 展示列表
  formList.classList.remove('hide')
  requestForm.classList.add('hide')
}

let popup = document.querySelector('.popup_shadow')
// 事件委托：点击活动进入请假填写页面
document.querySelector('.activity_items ').addEventListener('click', e => {
  let activity = e.target.closest('li.item')
  // toRequestForm(activity)
  if (activity) {
    // 若点击的是已结束的请假申请，弹框提示“无法点击”
    if (activity.classList.contains('ended')) {
      popup.querySelector('.top').innerHTML = '无法点击！'
      popup.classList.remove('hide')
    }
    // 若点击的是进行中的请假申请，跳转到请假申请编辑，并在 URL 后面拼接 activity 的名称
    else {
      let activityName = activity.querySelector('.activity_name').innerHTML

      // 展示请假单
      // 判断是否展示添加照片栏
      let isPhoto = false
      if (activity.classList.contains('photo_needed')) isPhoto = true
      // 活动名称
      document.querySelector('.header h2').innerHTML = activityName + '请假表'
      // 发送请求，查看是否已有填写记录
      getData(activity.id)
      // 页面切换
      // 修改 URL
      location.href = location.href + `#requestForm?isphoto=${isPhoto}&event_id=${activity.id}`
      // formList.classList.add('hide')
      // requestForm.classList.remove('hide')
    }
  }
})

// 监听到页面url发生变化时
window.addEventListener('popstate', () => {
  // 确保展示到正确的页面上
  pageUrl = location.href.split('#')[1]
  if (pageUrl) {
    // 展示请假单
    formList.classList.add('hide')
    is_photo_needed()
    requestForm.classList.remove('hide')
  } else {
    // 展示列表
    formList.classList.remove('hide')
    requestForm.classList.add('hide')
  }
  // 展示到对应页面时执行相应操作
})

// 点击“确认”移除提示框
popup.addEventListener('click', e => {
  if (e.target.classList.contains('close')) {
    popup.classList.add('hide')
  }
})
